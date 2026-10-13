
import argparse
import time
import webbrowser
from pathlib import Path

import serial

from audio.youtube_audio import download_audio
from audio.audio_analysis import analyze_audio


PROJECT_ROOT = Path(__file__).resolve().parent

DEFAULT_PORT = "/dev/cu.usbserial-0001"
BAUD_RATE = 115200


def main():
    parser = argparse.ArgumentParser(
        description="PayAttentionToFooty YouTube Haptics"
    )

    parser.add_argument(
        "--url",
        help="YouTube soccer video URL"
    )

    parser.add_argument(
        "--port",
        default=DEFAULT_PORT,
        help="ESP32 serial port"
    )

    parser.add_argument(
        "--max-pwm",
        type=int,
        default=100,
        help="Maximum motor PWM (0-255)"
    )

    args = parser.parse_args()

    if not 0 <= args.max_pwm <= 255:
        parser.error("--max-pwm must be 0-255")

    url = args.url or input(
        "Enter YouTube soccer video URL: "
    ).strip()

    if not url:
        parser.error("YouTube URL is required")

    # Step 1: Download fresh audio
    print("\nDownloading soccer audio...")

    audio_path, video_id = download_audio(
        url,
        output_dir=PROJECT_ROOT / "audio_samples"
    )

    print(f"Downloaded: {audio_path.name}")

    # Step 2: Analyze audio
    print("\nAnalyzing audio...")

    timeline = analyze_audio(audio_path)

    print(f"Generated {len(timeline)} haptic samples")

    # Step 3: Connect to ESP32
    print(f"\nConnecting to ESP32: {args.port}")

    esp32 = serial.Serial(
        args.port,
        BAUD_RATE,
        timeout=1,
        write_timeout=1
    )

    # ESP32 may restart when serial opens
    time.sleep(2)

    def send_pwm(value):
        value = max(0, min(args.max_pwm, int(value)))
        esp32.write(f"{value}\n".encode())

    try:
        send_pwm(0)

        # Step 4: Open YouTube video
        print("\nOpening YouTube in your browser...")

        webbrowser.open_new_tab(url)

        print(
            "\nPause the video at 0:00."
            "\nWhen ready, start the video and "
            "immediately press Enter here."
        )

        input("\nPress Enter to start haptics...")

        # Step 5: Play haptic timeline
        start_time = time.monotonic()

        print("\nHaptic playback started!")
        print("Press Ctrl+C to stop.\n")

        for timestamp, raw_pwm in timeline:

            target_time = start_time + timestamp

            remaining = target_time - time.monotonic()

            if remaining > 0:
                time.sleep(remaining)

            # Scale PWM to configured maximum
            pwm = round(
                raw_pwm * args.max_pwm / 255
            )

            send_pwm(pwm)

            print(
                f"Time: {timestamp:7.1f}s | "
                f"PWM: {pwm:3d}"
            )

    except KeyboardInterrupt:
        print("\nHaptic playback interrupted")

    finally:
        send_pwm(0)
        esp32.close()
        print("ESP32 disconnected. Motor stopped.")


if __name__ == "__main__":
    main()
