
import argparse
import asyncio
import json
import time

import serial
from websockets.asyncio.server import serve


async def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--port",
        required=True,
        help="ESP32 serial port"
    )

    parser.add_argument(
        "--max-pwm",
        type=int,
        default=100
    )

    args = parser.parse_args()

    if not 0 <= args.max_pwm <= 255:
        parser.error("--max-pwm must be 0-255")

    esp32 = serial.Serial(
        args.port,
        baudrate=115200,
        timeout=0.1,
        write_timeout=0.2
    )

    await asyncio.sleep(2)

    last_command = time.monotonic()
    last_pwm = 0
    active_client = None

    def send_pwm(value):
        nonlocal last_command, last_pwm

        value = max(
            0,
            min(args.max_pwm, int(value))
        )

        esp32.write(f"{value}\n".encode())

        last_pwm = value
        last_command = time.monotonic()

    async def watchdog():
        nonlocal last_pwm

        while True:
            await asyncio.sleep(0.1)

            if time.monotonic() - last_command > 0.4:
                if last_pwm != 0:
                    send_pwm(0)

    async def handler(websocket):
        nonlocal active_client

        origin = websocket.request.headers.get(
            "Origin", ""
        )

        allowed_origins = {
            "http://localhost:8501",
            "http://127.0.0.1:8501"
        }

        if origin not in allowed_origins:
            await websocket.close(
                code=1008,
                reason="Origin not allowed"
            )
            return

        if active_client is not None:
            await websocket.close(
                code=1008,
                reason="Another dashboard is connected"
            )
            return

        active_client = websocket
        print("Dashboard connected")

        try:
            async for message in websocket:
                try:
                    data = json.loads(message)

                    if data.get("type") != "pwm":
                        continue

                    value = data.get("value")

                    if (
                        type(value) not in (int, float)
                        or not 0 <= value <= 255
                    ):
                        continue

                    send_pwm(value)

                except (ValueError, TypeError):
                    continue

        finally:
            send_pwm(0)
            active_client = None
            print("Dashboard disconnected")

    try:
        send_pwm(0)

        async with serve(
            handler,
            "127.0.0.1",
            8765,
            max_size=4096
        ):
            print("ESP32 bridge running")
            print("Listening on ws://127.0.0.1:8765")

            await watchdog()

    finally:
        send_pwm(0)
        esp32.close()


if __name__ == "__main__":
    asyncio.run(main())
