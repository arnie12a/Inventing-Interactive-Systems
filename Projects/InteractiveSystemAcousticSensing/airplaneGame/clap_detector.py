import queue
import time

import numpy as np
import sounddevice as sd
from scipy.signal import get_window


class ClapDetector:
    """
    Detects claps and double claps from microphone input.

    Events produced:

        ("clap", strength)

        ("double_clap", strength)

    strength is approximately 0.0 - 1.0.
    """

    def __init__(
        self,
        sample_rate=48_000,
        block_size=1024,
        fft_size=4096,
        input_device=None,
    ):
        self.sample_rate = sample_rate
        self.block_size = block_size
        self.fft_size = fft_size
        self.input_device = input_device

        # --------------------------------------------------
        # CLAP DETECTION SETTINGS
        # --------------------------------------------------

        # Minimum microphone RMS level
        self.energy_threshold = 0.045

        # Frequency range used to identify a clap
        self.high_freq_min = 2000
        self.high_freq_max = 10000

        # Fraction of FFT energy that must be in the
        # high-frequency range.
        self.high_freq_ratio_threshold = 0.18

        # Prevent a single physical clap from triggering
        # multiple times.
        self.clap_cooldown = 0.15

        # Maximum time between two claps
        # for them to count as a double clap.
        self.double_clap_interval = 0.50

        # Used to normalize strength
        self.max_rms = 0.50

        # --------------------------------------------------
        # AUDIO QUEUE
        # --------------------------------------------------

        self.audio_queue = queue.Queue(maxsize=50)

        # --------------------------------------------------
        # EVENT QUEUE
        # --------------------------------------------------

        self.event_queue = queue.Queue()

        # --------------------------------------------------
        # DOUBLE CLAP STATE
        # --------------------------------------------------

        self.first_clap_time = None
        self.first_clap_strength = None

        # --------------------------------------------------
        # COOLDOWN
        # --------------------------------------------------

        self.last_clap_time = 0.0

        # --------------------------------------------------
        # FFT
        # --------------------------------------------------

        self.window = get_window(
            "hann",
            self.fft_size
        )

        self.frequency_bins = np.fft.rfftfreq(
            self.fft_size,
            1 / self.sample_rate
        )

        # --------------------------------------------------
        # STREAM
        # --------------------------------------------------

        self.stream = None

    # ======================================================
    # MICROPHONE CALLBACK
    # ======================================================

    def _audio_callback(
        self,
        indata,
        frames,
        time_info,
        status
    ):
        """
        Called automatically by sounddevice.
        """

        if status:
            print("Audio status:", status)

        block = indata[:, 0].copy()

        try:

            self.audio_queue.put_nowait(block)

        except queue.Full:

            try:
                self.audio_queue.get_nowait()
                self.audio_queue.put_nowait(block)

            except queue.Empty:
                pass

    # ======================================================
    # START MICROPHONE
    # ======================================================

    def start(self):

        self.stream = sd.InputStream(
            samplerate=self.sample_rate,
            blocksize=self.block_size,
            dtype="float32",
            channels=1,
            device=self.input_device,
            callback=self._audio_callback,
            latency="low",
        )

        self.stream.start()

    # ======================================================
    # STOP MICROPHONE
    # ======================================================

    def stop(self):

        if self.stream is not None:

            self.stream.stop()
            self.stream.close()

            self.stream = None

    # ======================================================
    # CALCULATE CLAP STRENGTH
    # ======================================================

    def _calculate_strength(self, rms):

        strength = rms / self.max_rms

        return float(
            np.clip(
                strength,
                0.0,
                1.0
            )
        )

    # ======================================================
    # DETECT INDIVIDUAL CLAP
    # ======================================================

    def _detect_clap(self, block):
        """
        Return clap strength if this audio block
        looks like a new clap.

        Return None otherwise.
        """

        # --------------------------------------------------
        # Remove DC offset
        # --------------------------------------------------

        block = block - np.mean(block)

        # --------------------------------------------------
        # RMS
        # --------------------------------------------------

        rms = np.sqrt(
            np.mean(block ** 2)
        )

        # Too quiet
        if rms < self.energy_threshold:
            return None

        # --------------------------------------------------
        # Zero pad to FFT size
        # --------------------------------------------------

        padded = np.zeros(
            self.fft_size,
            dtype=np.float32
        )

        n = min(
            len(block),
            self.fft_size
        )

        padded[-n:] = block[-n:]

        # --------------------------------------------------
        # Window
        # --------------------------------------------------

        windowed = padded * self.window

        # --------------------------------------------------
        # FFT
        # --------------------------------------------------

        spectrum = np.fft.rfft(
            windowed
        )

        power = np.abs(
            spectrum
        ) ** 2

        # --------------------------------------------------
        # Total spectral energy
        # --------------------------------------------------

        total_energy = np.sum(power)

        if total_energy <= 0:
            return None

        # --------------------------------------------------
        # High frequency energy
        # --------------------------------------------------

        high_frequency_mask = (
            (self.frequency_bins >= self.high_freq_min)
            &
            (self.frequency_bins <= self.high_freq_max)
        )

        high_frequency_energy = np.sum(
            power[high_frequency_mask]
        )

        high_frequency_ratio = (
            high_frequency_energy
            / total_energy
        )

        # --------------------------------------------------
        # Clap frequency requirement
        # --------------------------------------------------

        if (
            high_frequency_ratio
            < self.high_freq_ratio_threshold
        ):
            return None

        # --------------------------------------------------
        # Cooldown
        # --------------------------------------------------

        now = time.monotonic()

        if (
            now - self.last_clap_time
            < self.clap_cooldown
        ):
            return None

        self.last_clap_time = now

        # --------------------------------------------------
        # Strength
        # --------------------------------------------------

        strength = self._calculate_strength(
            rms
        )

        return strength

    # ======================================================
    # PROCESS CLAP
    # ======================================================

    def _process_clap(self, strength):

        now = time.monotonic()

        # --------------------------------------------------
        # First clap
        # --------------------------------------------------

        if self.first_clap_time is None:

            self.first_clap_time = now
            self.first_clap_strength = strength

            return

        # --------------------------------------------------
        # Second clap
        # --------------------------------------------------

        interval = (
            now - self.first_clap_time
        )

        if interval <= self.double_clap_interval:

            # Average strength of both claps
            double_strength = (
                self.first_clap_strength
                + strength
            ) / 2.0

            self.event_queue.put(
                (
                    "double_clap",
                    double_strength
                )
            )

            self.first_clap_time = None
            self.first_clap_strength = None

        # --------------------------------------------------
        # Too slow -> previous was single clap
        # --------------------------------------------------

        else:

            self.event_queue.put(
                (
                    "clap",
                    self.first_clap_strength
                )
            )

            self.first_clap_time = now
            self.first_clap_strength = strength

    # ======================================================
    # UPDATE
    # ======================================================

    def update(self):

        # --------------------------------------------------
        # Process microphone blocks
        # --------------------------------------------------

        while True:

            try:

                block = self.audio_queue.get_nowait()

            except queue.Empty:

                break

            strength = self._detect_clap(block)

            if strength is not None:

                self._process_clap(
                    strength
                )

        # --------------------------------------------------
        # Check whether a pending clap became
        # a single clap.
        # --------------------------------------------------

        if self.first_clap_time is not None:

            elapsed = (
                time.monotonic()
                - self.first_clap_time
            )

            if elapsed > self.double_clap_interval:

                self.event_queue.put(
                    (
                        "clap",
                        self.first_clap_strength
                    )
                )

                self.first_clap_time = None
                self.first_clap_strength = None

    # ======================================================
    # GET EVENTS
    # ======================================================

    def get_events(self):

        events = []

        while True:

            try:

                event = (
                    self.event_queue.get_nowait()
                )

                events.append(event)

            except queue.Empty:

                break

        return events