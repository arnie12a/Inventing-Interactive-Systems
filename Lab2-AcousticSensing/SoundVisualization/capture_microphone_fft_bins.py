"""
Records audio input using the microphone and displays a live FFT plot.

The X-axis shows frequency in Hz.
The Y-axis shows amplitude in dB.
The peak frequency and amplitude are displayed on the plot.
"""

import queue

import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from scipy.signal import get_window


# -----------------------------
# Audio configuration
# -----------------------------
SAMPLE_RATE = 96_000
BLOCK_SIZE = 1024
CHANNELS = 1

# FFT settings
FFT_SIZE = 4096

# Display frequency range
DISPLAY_MIN_FREQUENCY = 0
DISPLAY_MAX_FREQUENCY = 22050

# CHANGE THIS TO MATCH YOUR SYSTEM
INPUT_DEVICE = 0


# -----------------------------
# Audio callback
# -----------------------------
audio_queue = queue.Queue(maxsize=50)


def audio_callback(indata, outdata, frames, time_info, status):
    if status:
        print(status)

    try:
        audio_queue.put_nowait(indata[:, 0].copy())
    except queue.Full:
        try:
            audio_queue.get_nowait()
            audio_queue.put_nowait(indata[:, 0].copy())
        except queue.Empty:
            pass


# -----------------------------
# FFT setup
# -----------------------------

# Frequencies corresponding to each FFT bin
frequency_bins = np.fft.rfftfreq(
    FFT_SIZE,
    1 / SAMPLE_RATE
)

# Find bins corresponding to requested display range
min_bin = np.searchsorted(
    frequency_bins,
    DISPLAY_MIN_FREQUENCY,
)

max_bin = np.searchsorted(
    frequency_bins,
    DISPLAY_MAX_FREQUENCY,
)

frequency_bins_display = frequency_bins[min_bin:max_bin]

# Hann window
window = get_window("hann", FFT_SIZE)


# -----------------------------
# Compute FFT
# -----------------------------
def compute_fft(block):
    """Return magnitude spectrum in dB."""

    # Zero-pad if block is smaller than FFT_SIZE
    if len(block) < FFT_SIZE:
        padded = np.zeros(FFT_SIZE, dtype=np.float32)
        padded[-len(block):] = block
        block = padded
    else:
        block = block[-FFT_SIZE:]

    # Remove DC offset
    block = block - np.mean(block)

    # Apply Hann window
    windowed_block = block * window

    # Compute FFT
    spectrum = np.fft.rfft(windowed_block)

    # Convert to magnitude
    magnitude = np.abs(spectrum) / np.sum(window)

    # Convert to dB
    magnitude_db = 20 * np.log10(
        np.maximum(magnitude, 1e-10)
    )

    return magnitude_db[min_bin:max_bin]


# -----------------------------
# Plot update
# -----------------------------
def update_plot(_frame):

    latest_fft = None

    # Process all available microphone blocks.
    # If several are waiting, use the most recent one.
    while True:
        try:
            block = audio_queue.get_nowait()
            latest_fft = compute_fft(block)
        except queue.Empty:
            break

    if latest_fft is not None:

        # Update FFT line
        line.set_ydata(latest_fft)

        # Find frequency bin with highest amplitude
        peak_index = np.argmax(latest_fft)

        peak_frequency = frequency_bins_display[peak_index]
        peak_amplitude = latest_fft[peak_index]

        # Update text
        peak_text.set_text(
            f"Peak Frequency: {peak_frequency:7.1f} Hz\n"
            f"Amplitude:      {peak_amplitude:7.1f} dB"
        )


        # Move marker to peak
        peak_marker.set_data(
            [peak_frequency],
            [peak_amplitude]
        )

    return line, peak_text, peak_marker


# -----------------------------
# Start audio stream and plot
# -----------------------------

print("Available audio devices:")
print(sd.query_devices())

print("\nStarting microphone FFT.")
print("Close the plot window or press Ctrl+C to stop.")


fig, ax = plt.subplots(figsize=(11, 6))


# Initial FFT values
initial_fft = np.full(
    len(frequency_bins_display),
    -100.0
)


# FFT line
line, = ax.plot(
    frequency_bins_display,
    initial_fft,
    color="blue",
    linewidth=1.5,
)


# Peak marker
peak_marker, = ax.plot(
    [0],
    [-100],
    marker="o",
    markersize=8,
    color="purple",
    linestyle="None",
)


# -----------------------------
# Peak frequency text
# -----------------------------

peak_text = ax.text(
    0.02,
    0.95,
    "Peak Frequency: ----- Hz\nAmplitude:      ---.-- dB",
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


# -----------------------------
# Plot configuration
# -----------------------------

ax.set_title("Live Microphone FFT")
ax.set_xlabel("Frequency (Hz)")
ax.set_ylabel("Amplitude (dB)")

ax.set_xlim(
    DISPLAY_MIN_FREQUENCY,
    DISPLAY_MAX_FREQUENCY
)

ax.set_ylim(-100, 0)

ax.grid(True, alpha=0.3)


# -----------------------------
# Open audio stream
# -----------------------------

stream = sd.Stream(
    samplerate=SAMPLE_RATE,
    blocksize=BLOCK_SIZE,
    dtype="float32",
    channels=(CHANNELS, CHANNELS),
    device=(INPUT_DEVICE, None),
    callback=audio_callback,
    latency="low",
)


# -----------------------------
# Run
# -----------------------------

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