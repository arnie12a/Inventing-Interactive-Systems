import queue
import time

import numpy as np
import sounddevice as sd
from scipy.signal import get_window


class ClapDetector:

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

        # ==================================================
        # CLAP DETECTION SETTINGS
        # ==================================================

        # Lower = more sensitive
        self.energy_threshold = 0.025

        # Frequency range associated with clap energy
        self.high_freq_min = 1500
        self.high_freq_max = 12000

        # Lower = easier to trigger
        self.high_freq_ratio_threshold = 0.12

        # Prevent one clap from triggering multiple times
        self.clap_cooldown = 0.12

        # Maximum time between claps for double clap
        self.double_clap_interval = 0.50

        # ==================================================
        # STRENGTH SETTINGS
        # ==================================================

        self.max_rms = 0.25

        self.noise_floor = 0.01

        # Makes loud claps more valuable
        self.strength_exponent = 1.5

        # ==================================================
        # QUEUES
        # ==================================================

        self.audio_queue = queue.Queue(
            maxsize=50
        )

        self.event_queue = queue.Queue()

        # ==================================================
        # CLAP STATE
        # ==================================================

        self.first_clap_time = None
        self.first_clap_strength = None

        self.last_clap_time = 0.0

        # ==================================================
        # FFT
        # ==================================================

        self.window = get_window(
            "hann",
            self.fft_size
        )

        self.frequency_bins = np.fft.rfftfreq(
            self.fft_size,
            1 / self.sample_rate
        )

        self.stream = None

    # ======================================================
    # AUDIO CALLBACK
    # ======================================================

    def _audio_callback(
        self,
        indata,
        frames,
        time_info,
        status
    ):
        if status:
            print(
                "Audio status:",
                status
            )

        block = (
            indata[:, 0].copy()
        )

        try:
            self.audio_queue.put_nowait(
                block
            )

        except queue.Full:

            try:
                self.audio_queue.get_nowait()

                self.audio_queue.put_nowait(
                    block
                )

            except queue.Empty:
                pass

    # ======================================================
    # START
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
    # STOP
    # ======================================================

    def stop(self):

        if self.stream is not None:

            self.stream.stop()
            self.stream.close()

            self.stream = None

    # ======================================================
    # STRENGTH
    # ======================================================

    def _calculate_strength(
        self,
        rms,
        peak
    ):
        adjusted_rms = max(
            0.0,
            rms - self.noise_floor
        )

        adjusted_peak = max(
            0.0,
            peak - self.noise_floor
        )

        denominator = (
            self.max_rms
            - self.noise_floor
        )

        rms_strength = (
            adjusted_rms
            / denominator
        )

        peak_strength = (
            adjusted_peak
            / denominator
        )

        rms_strength = float(
            np.clip(
                rms_strength,
                0.0,
                1.0
            )
        )

        peak_strength = float(
            np.clip(
                peak_strength,
                0.0,
                1.0
            )
        )

        # RMS gets more weight.
        raw_strength = (
            0.75 * rms_strength
            + 0.25 * peak_strength
        )

        # Emphasize stronger claps.
        strength = (
            raw_strength
            ** self.strength_exponent
        )

        return float(
            np.clip(
                strength,
                0.0,
                1.0
            )
        )

    # ======================================================
    # DETECT CLAP
    # ======================================================

    def _detect_clap(
        self,
        block
    ):
        # Remove DC offset
        block = (
            block
            - np.mean(block)
        )

        # ==================================================
        # RMS
        # ==================================================

        rms = np.sqrt(
            np.mean(
                block ** 2
            )
        )

        # ==================================================
        # PEAK
        # ==================================================

        peak = np.max(
            np.abs(block)
        )

        # Too quiet
        if rms < self.energy_threshold:
            return None

        # ==================================================
        # FFT
        # ==================================================

        padded = np.zeros(
            self.fft_size,
            dtype=np.float32
        )

        n = min(
            len(block),
            self.fft_size
        )

        padded[-n:] = block[-n:]

        windowed = (
            padded
            * self.window
        )

        spectrum = np.fft.rfft(
            windowed
        )

        power = (
            np.abs(spectrum)
            ** 2
        )

        total_energy = np.sum(
            power
        )

        if total_energy <= 0:
            return None

        # ==================================================
        # HIGH FREQUENCY ENERGY
        # ==================================================

        high_frequency_mask = (
            (
                self.frequency_bins
                >= self.high_freq_min
            )
            &
            (
                self.frequency_bins
                <= self.high_freq_max
            )
        )

        high_frequency_energy = np.sum(
            power[
                high_frequency_mask
            ]
        )

        high_frequency_ratio = (
            high_frequency_energy
            / total_energy
        )

        if (
            high_frequency_ratio
            < self.high_freq_ratio_threshold
        ):
            return None

        # ==================================================
        # COOLDOWN
        # ==================================================

        now = time.monotonic()

        if (
            now - self.last_clap_time
            < self.clap_cooldown
        ):
            return None

        self.last_clap_time = now

        # ==================================================
        # STRENGTH
        # ==================================================

        strength = (
            self._calculate_strength(
                rms,
                peak
            )
        )

        print(
            f"Clap detected"
            f" | RMS={rms:.4f}"
            f" | Peak={peak:.4f}"
            f" | HF={high_frequency_ratio:.2f}"
            f" | Strength={strength:.2f}"
        )

        return strength

    # ======================================================
    # PROCESS CLAP SEQUENCE
    # ======================================================

    def _process_clap(
        self,
        strength
    ):
        now = time.monotonic()

        # First clap
        if self.first_clap_time is None:

            self.first_clap_time = now

            self.first_clap_strength = (
                strength
            )

            return

        interval = (
            now
            - self.first_clap_time
        )

        # ==================================================
        # DOUBLE CLAP
        # ==================================================

        if (
            interval
            <= self.double_clap_interval
        ):
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

            print(
                f"DOUBLE CLAP"
                f" | first="
                f"{self.first_clap_strength:.2f}"
                f" | second="
                f"{strength:.2f}"
                f" | average="
                f"{double_strength:.2f}"
            )

            self.first_clap_time = None
            self.first_clap_strength = None

        # ==================================================
        # PREVIOUS CLAP WAS SINGLE
        # ==================================================

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

        # Process microphone blocks
        while True:

            try:
                block = (
                    self.audio_queue.get_nowait()
                )

            except queue.Empty:
                break

            strength = (
                self._detect_clap(
                    block
                )
            )

            if strength is not None:

                self._process_clap(
                    strength
                )

        # ==================================================
        # PENDING SINGLE CLAP
        # ==================================================

        if (
            self.first_clap_time
            is not None
        ):
            elapsed = (
                time.monotonic()
                - self.first_clap_time
            )

            if (
                elapsed
                > self.double_clap_interval
            ):
                self.event_queue.put(
                    (
                        "clap",
                        self.first_clap_strength
                    )
                )

                print(
                    f"SINGLE CLAP"
                    f" | strength="
                    f"{self.first_clap_strength:.2f}"
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
                events.append(
                    self.event_queue.get_nowait()
                )

            except queue.Empty:
                break

        return events