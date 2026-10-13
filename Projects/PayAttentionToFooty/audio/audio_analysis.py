
import numpy as np
import soundfile as sf


def analyze_audio(audio_path, window_ms=100):
    audio, sample_rate = sf.read(
        str(audio_path),
        dtype="float32",
        always_2d=True
    )

    audio = audio.mean(axis=1)

    window_size = max(
        1,
        int(sample_rate * window_ms / 1000)
    )

    rms_values = []

    for start in range(0, len(audio), window_size):
        chunk = audio[start:start + window_size]

        if len(chunk) == 0:
            continue

        rms = np.sqrt(
            np.mean(chunk.astype("float64") ** 2)
        )

        rms_values.append(rms)

    if not rms_values:
        raise ValueError("No audio samples found")

    rms_values = np.asarray(rms_values)

    db_values = 20 * np.log10(
        np.maximum(rms_values, 1e-8)
    )

    quiet = np.percentile(db_values, 20)
    loud = np.percentile(db_values, 95)

    energy = np.clip(
        (db_values - quiet) / max(loud - quiet, 1e-6),
        0,
        1
    )

    # Smooth the vibration signal
    smoothed = np.zeros_like(energy)
    smoothed[0] = energy[0]

    for i in range(1, len(energy)):
        smoothed[i] = (
            0.3 * energy[i]
            + 0.7 * smoothed[i - 1]
        )

    pwm = np.round(smoothed * 255).astype(int)

    return [
        (i * window_ms / 1000, int(value))
        for i, value in enumerate(pwm)
    ]
