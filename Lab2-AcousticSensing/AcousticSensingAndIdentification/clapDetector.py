"""
Live microphone FFT with single-clap and double-clap detection.

The program:
1. Captures microphone audio.
2. Computes and displays the FFT.
3. Detects individual clap events.
4. Uses the timing between clap events to distinguish:
       CLAP
       DOUBLE CLAP
"""

import queue
import time

import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from scipy.signal import get_window


# ============================================================
# AUDIO CONFIGURATION
# ============================================================

SAMPLE_RATE = 96_000
BLOCK_SIZE = 2048
CHANNELS = 1

# FFT size used for visualization/detection
FFT_SIZE = 4096

# Frequency range shown on screen
DISPLAY_MIN_FREQUENCY = 0
DISPLAY_MAX_FREQUENCY = 22050

# Change this to your microphone device
INPUT_DEVICE = 0


# ============================================================
# CLAP DETECTION SETTINGS
# ============================================================

# Minimum RMS amplitude needed to consider the sound significant.
# This value will probably need to be tuned for your microphone.
ENERGY_THRESHOLD = 0.05

# High-frequency range used to help identify a clap.
HIGH_FREQ_MIN = 2000
HIGH_FREQ_MAX = 10000

# Minimum percentage of spectral energy that must be
# inside the high-frequency range.
HIGH_FREQ_RATIO_THRESHOLD = 0.20

# Once a clap is detected, ignore additional detections
# for this amount of time.
#
# This prevents ONE clap from being detected several times.
CLAP_COOLDOWN = 0.15

# Maximum amount of time allowed between two claps
# for them to count as a double clap.
DOUBLE_CLAP_INTERVAL = 0.50


# ============================================================
# STATE VARIABLES
# ============================================================

# Most recent actual clap detection time
last_clap_time = 0

# Time of the first clap when waiting to see
# whether another clap follows.
first_clap_time = None

# Current detection state
#
# WAITING:
#   We are waiting for the first clap.
#
# WAITING_FOR_SECOND:
#   We have detected one clap and are waiting to see
#   whether another clap occurs soon enough.
state = "WAITING"


# ============================================================
# AUDIO QUEUE
# ============================================================

audio_queue = queue.Queue(maxsize=50)


def audio_callback(indata, outdata, frames, time_info, status):
    """
    Called automatically whenever new microphone
    audio is available.
    """

    if status:
        print(status)

    try:
        # Save the microphone data in the queue.
        audio_queue.put_nowait(
            indata[:, 0].copy()
        )

    except queue.Full:

        # If the queue fills up, discard the oldest
        # block so that we keep processing recent audio.
        try:
            audio_queue.get_nowait()

            audio_queue.put_nowait(
                indata[:, 0].copy()
            )

        except queue.Empty:
            pass


# ============================================================
# FFT SETUP
# ============================================================

# Frequency corresponding to each FFT bin
frequency_bins = np.fft.rfftfreq(
    FFT_SIZE,
    1 / SAMPLE_RATE
)

# Find bins corresponding to display range
min_bin = np.searchsorted(
    frequency_bins,
    DISPLAY_MIN_FREQUENCY
)

max_bin = np.searchsorted(
    frequency_bins,
    DISPLAY_MAX_FREQUENCY
)

frequency_bins_display = frequency_bins[
    min_bin:max_bin
]

# Hann window for FFT
window = get_window(
    "hann",
    FFT_SIZE
)


# ============================================================
# COMPUTE FFT
# ============================================================

def compute_fft(block):
    """
    Compute the FFT magnitude in dB.
    """

    # --------------------------------------------------------
    # Zero-pad if the block is shorter than FFT_SIZE
    # --------------------------------------------------------

    if len(block) < FFT_SIZE:

        padded = np.zeros(
            FFT_SIZE,
            dtype=np.float32
        )

        padded[-len(block):] = block

        block = padded

    else:

        block = block[-FFT_SIZE:]

    # --------------------------------------------------------
    # Remove DC offset
    # --------------------------------------------------------

    block = block - np.mean(block)

    # --------------------------------------------------------
    # Apply Hann window
    # --------------------------------------------------------

    windowed_block = (
        block * window
    )

    # --------------------------------------------------------
    # FFT
    # --------------------------------------------------------

    spectrum = np.fft.rfft(
        windowed_block
    )

    # --------------------------------------------------------
    # Magnitude
    # --------------------------------------------------------

    magnitude = (
        np.abs(spectrum)
        / np.sum(window)
    )

    # --------------------------------------------------------
    # Convert to dB
    # --------------------------------------------------------

    magnitude_db = 20 * np.log10(
        np.maximum(
            magnitude,
            1e-10
        )
    )

    return magnitude_db[
        min_bin:max_bin
    ]


# ============================================================
# DETECT INDIVIDUAL CLAP
# ============================================================

def detect_clap(block):
    """
    Determine whether a microphone block looks like a clap.

    Returns:
        True  -> new clap detected
        False -> no new clap detected
    """

    global last_clap_time

    # --------------------------------------------------------
    # 1. Remove DC offset
    # --------------------------------------------------------

    block = block - np.mean(block)

    # --------------------------------------------------------
    # 2. Calculate RMS energy
    # --------------------------------------------------------

    rms = np.sqrt(
        np.mean(block ** 2)
    )

    # The signal must be loud enough
    # before we consider it a potential clap.
    if rms < ENERGY_THRESHOLD:
        return False

    # --------------------------------------------------------
    # 3. Compute FFT
    # --------------------------------------------------------

    # The actual block may be smaller than FFT_SIZE,
    # so let NumPy zero-pad it automatically.
    windowed = (
        block * window[:len(block)]
    )

    spectrum = np.fft.rfft(
        windowed,
        n=FFT_SIZE
    )

    # --------------------------------------------------------
    # 4. Calculate spectral power
    # --------------------------------------------------------

    power = np.abs(
        spectrum
    ) ** 2

    # Frequency corresponding to each FFT bin
    freqs = np.fft.rfftfreq(
        FFT_SIZE,
        1 / SAMPLE_RATE
    )

    # --------------------------------------------------------
    # 5. Total spectral energy
    # --------------------------------------------------------

    total_energy = np.sum(power)

    if total_energy <= 0:
        return False

    # --------------------------------------------------------
    # 6. High-frequency energy
    # --------------------------------------------------------

    high_freq_mask = (
        (freqs >= HIGH_FREQ_MIN)
        &
        (freqs <= HIGH_FREQ_MAX)
    )

    high_freq_energy = np.sum(
        power[high_freq_mask]
    )

    # --------------------------------------------------------
    # 7. Calculate ratio
    # --------------------------------------------------------

    high_freq_ratio = (
        high_freq_energy
        / total_energy
    )

    # --------------------------------------------------------
    # 8. Check whether this looks like a clap
    # --------------------------------------------------------

    if high_freq_ratio < HIGH_FREQ_RATIO_THRESHOLD:
        return False

    # --------------------------------------------------------
    # 9. Cooldown
    # --------------------------------------------------------

    current_time = time.time()

    if (
        current_time - last_clap_time
        < CLAP_COOLDOWN
    ):
        return False

    # --------------------------------------------------------
    # New clap!
    # --------------------------------------------------------

    last_clap_time = current_time

    print(
        f"Clap detected "
        f"(RMS={rms:.3f}, "
        f"high_freq_ratio={high_freq_ratio:.2f})"
    )

    return True


# ============================================================
# PROCESS CLAP PATTERN
# ============================================================

def process_clap(clap_detected):
    """
    Determine whether a clap is:
        CLAP
        DOUBLE CLAP
    """

    global state
    global first_clap_time

    current_time = time.time()

    # ========================================================
    # WAITING FOR FIRST CLAP
    # ========================================================

    if state == "WAITING":

        if clap_detected:

            # Save time of first clap
            first_clap_time = current_time

            # Now wait for another clap
            state = "WAITING_FOR_SECOND"

            return None

    # ========================================================
    # WAITING FOR SECOND CLAP
    # ========================================================

    elif state == "WAITING_FOR_SECOND":

        # ----------------------------------------------------
        # Another clap happened
        # ----------------------------------------------------

        if clap_detected:

            interval = (
                current_time
                - first_clap_time
            )

            # ------------------------------------------------
            # Two claps close together
            # ------------------------------------------------

            if interval <= DOUBLE_CLAP_INTERVAL:

                print(
                    f"DOUBLE CLAP "
                    f"({interval:.3f} seconds apart)"
                )

                state = "WAITING"
                first_clap_time = None

                return "DOUBLE CLAP"

            # ------------------------------------------------
            # This clap was too far away
            #
            # Treat previous clap as a single clap.
            # This new clap becomes the beginning of
            # another possible double clap.
            # ------------------------------------------------

            else:

                print("CLAP")

                first_clap_time = current_time

                state = "WAITING_FOR_SECOND"

                return "CLAP"

        # ----------------------------------------------------
        # No second clap yet
        # ----------------------------------------------------

        elif (
            current_time - first_clap_time
            > DOUBLE_CLAP_INTERVAL
        ):

            # Timeout means it was just one clap.
            print("CLAP")

            state = "WAITING"
            first_clap_time = None

            return "CLAP"

    return None


# ============================================================
# PLOT UPDATE
# ============================================================

def update_plot(_frame):

    latest_fft = None
    latest_block = None

    # --------------------------------------------------------
    # Process all queued microphone blocks
    # --------------------------------------------------------

    while True:

        try:

            block = audio_queue.get_nowait()

            latest_block = block

            latest_fft = compute_fft(
                block
            )

        except queue.Empty:
            break

    # --------------------------------------------------------
    # Update visualization
    # --------------------------------------------------------

    if latest_fft is not None:

        # Update FFT line
        line.set_ydata(
            latest_fft
        )

        # Find strongest frequency
        peak_index = np.argmax(
            latest_fft
        )

        peak_frequency = (
            frequency_bins_display[
                peak_index
            ]
        )

        peak_amplitude = (
            latest_fft[
                peak_index
            ]
        )

        # Update peak text
        peak_text.set_text(
            f"Peak Frequency: "
            f"{peak_frequency:7.1f} Hz\n"
            f"Amplitude:      "
            f"{peak_amplitude:7.1f} dB"
        )

        # Move peak marker
        peak_marker.set_data(
            [peak_frequency],
            [peak_amplitude]
        )

    # --------------------------------------------------------
    # Detect clap
    # --------------------------------------------------------

    if latest_block is not None:

        clap_detected = detect_clap(
            latest_block
        )

        result = process_clap(
            clap_detected
        )

        # Update screen when a final gesture
        # classification is made.
        if result is not None:

            gesture_text.set_text(
                result
            )

    return (
        line,
        peak_text,
        peak_marker,
        gesture_text
    )


# ============================================================
# START PROGRAM
# ============================================================

print("Available audio devices:")
print(sd.query_devices())

print()
print("Starting microphone FFT.")
print()
print("Try the following:")
print("  One clap       -> CLAP")
print("  Two quick claps -> DOUBLE CLAP")
print()
print("Close the plot or press Ctrl+C to stop.")


# ============================================================
# CREATE FIGURE
# ============================================================

fig, ax = plt.subplots(
    figsize=(11, 6)
)


# ============================================================
# INITIAL FFT
# ============================================================

initial_fft = np.full(
    len(frequency_bins_display),
    -100.0
)


# ============================================================
# FFT LINE
# ============================================================

line, = ax.plot(
    frequency_bins_display,
    initial_fft,
    color="blue",
    linewidth=1.5,
)


# ============================================================
# PEAK MARKER
# ============================================================

peak_marker, = ax.plot(
    [0],
    [-100],
    marker="o",
    markersize=8,
    color="purple",
    linestyle="None",
)


# ============================================================
# PEAK TEXT
# ============================================================

peak_text = ax.text(
    0.02,
    0.95,

    "Peak Frequency: ----- Hz\n"
    "Amplitude:      ---.-- dB",

    transform=ax.transAxes,

    horizontalalignment="left",
    verticalalignment="top",

    fontsize=13,

    color="purple",

    family="monospace",

    bbox=dict(
        boxstyle="round",
        facecolor="white",
        alpha=0.8,
    ),
)


# ============================================================
# GESTURE TEXT
# ============================================================

gesture_text = ax.text(
    0.75,
    0.90,

    "WAITING",

    transform=ax.transAxes,

    horizontalalignment="center",
    verticalalignment="center",

    fontsize=24,
    fontweight="bold",

    color="black",
)


# ============================================================
# PLOT CONFIGURATION
# ============================================================

ax.set_title(
    "Live Microphone FFT + Clap Detection"
)

ax.set_xlabel(
    "Frequency (Hz)"
)

ax.set_ylabel(
    "Amplitude (dB)"
)

ax.set_xlim(
    DISPLAY_MIN_FREQUENCY,
    DISPLAY_MAX_FREQUENCY
)

ax.set_ylim(
    -100,
    0
)

ax.grid(
    True,
    alpha=0.3
)


# ============================================================
# OPEN AUDIO STREAM
# ============================================================

stream = sd.Stream(
    samplerate=SAMPLE_RATE,

    blocksize=BLOCK_SIZE,

    dtype="float32",

    channels=(
        CHANNELS,
        CHANNELS
    ),

    device=(
        INPUT_DEVICE,
        None
    ),

    callback=audio_callback,

    latency="low",
)


# ============================================================
# RUN
# ============================================================

try:

    with stream:

        animation = FuncAnimation(
            fig,

            update_plot,

            interval=50,

            blit=True,

            cache_frame_data=False,
        )

        plt.show()


except KeyboardInterrupt:

    pass


finally:

    plt.close(fig)

    print("Stopped.")