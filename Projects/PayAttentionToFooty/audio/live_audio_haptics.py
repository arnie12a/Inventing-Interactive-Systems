
import argparse
import time
import webbrowser

import numpy as np
import sounddevice as sd
import serial


# ==========================================
# ESP32 CONFIGURATION
# ==========================================

PORT = "/dev/cu.usbserial-0001"
BAUD_RATE = 115200

SAMPLE_RATE = 16000
BLOCK_MS = 100
BLOCK_SIZE = int(SAMPLE_RATE * BLOCK_MS / 1000)

MAX_PWM = 140

# ==========================================
# AUDIO CONFIGURATION
# ==========================================

# Ignore very quiet sounds
QUIET_THRESHOLD = -35

# Amplification factor
AMPLIFICATION = 3.5

# PWM below this value becomes zero
NOISE_GATE_PWM = 25

# Smooth vibration transitions
SMOOTHING = 0.55


# ==========================================
# AUDIO TO HAPTIC MAPPING
# ==========================================

def calculate_base_pwm(db):

    if db < QUIET_THRESHOLD:
        return 0

    elif db < -18:
        normalized = (db + 35) / 17
        return int(normalized * 30)

    elif db < -10:
        normalized = (db + 18) / 8
        return int(100 + normalized * 40)

    else:
        return 140


def calculate_pwm(db):

    # Original PWM calculation
    base_pwm = calculate_base_pwm(db)

    # Amplify
    amplified_pwm = int(
        base_pwm * AMPLIFICATION
    )

    # Cap at maximum
    amplified_pwm = min(
        amplified_pwm,
        MAX_PWM
    )

    # Remove weak background vibrations
    if amplified_pwm < NOISE_GATE_PWM:
        amplified_pwm = 0

    return amplified_pwm


# ==========================================
# MAIN APPLICATION
# ==========================================

def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--url",
        type=str,
        default=None
    )

    parser.add_argument(
        "--device",
        type=int,
        default=None
    )

    args = parser.parse_args()

    print("\nPayAttentionToFooty")
    print("Amplified Acoustic Haptics\n")

    print(f"Connecting to ESP32 on {PORT}...")

    esp32 = serial.Serial(
        PORT,
        BAUD_RATE,
        timeout=0.1,
        write_timeout=1
    )

    time.sleep(2)

    print("ESP32 connected!")

    def send_pwm(pwm):
        pwm = max(0, min(MAX_PWM, int(pwm)))
        esp32.write(f"{pwm}\n".encode())

    previous_pwm = 0

    try:
        send_pwm(0)

        if args.url:
            webbrowser.open_new_tab(args.url)

        print("Listening for soccer audio...")
        print("Press Ctrl+C to stop.\n")

        with sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=1,
            blocksize=BLOCK_SIZE,
            device=args.device
        ) as stream:

            while True:

                audio, overflowed = stream.read(BLOCK_SIZE)

                samples = audio[:, 0].astype(np.float64)

                rms = np.sqrt(
                    np.mean(samples ** 2)
                )

                db = 20 * np.log10(
                    max(rms, 1e-8)
                )

                target_pwm = calculate_pwm(db)

                # Smooth changes
                smoothed_pwm = int(
                    SMOOTHING * target_pwm
                    + (1 - SMOOTHING) * previous_pwm
                )

                previous_pwm = smoothed_pwm

                send_pwm(smoothed_pwm)

                print(
                    f"Loudness: {db:6.1f} dBFS | "
                    f"PWM: {smoothed_pwm:3d} / 140",
                    end="\r",
                    flush=True
                )

                if overflowed:
                    print("\nAudio input overflow")

    except KeyboardInterrupt:
        print("\nStopping...")

    finally:
        send_pwm(0)
        esp32.close()
        print("Motor stopped.")


if __name__ == "__main__":
    main()



# python3 audio/live_audio_haptics.py --url "https://www.youtube.com/watch?v=ydx1L0aDj_c"