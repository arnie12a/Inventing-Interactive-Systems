
import serial
import time


class HapticController:
    def __init__(self, port, baudrate=115200):
        self.serial = serial.Serial(
            port,
            baudrate,
            timeout=1
        )

        # Allow ESP32 to restart
        time.sleep(2)

        print(f"ESP32 connected on {port}")

    def send_intensity(self, intensity):
        """
        Send PWM value between 0 and 255.
        """
        intensity = max(
            0, min(255, int(intensity))
        )

        message = f"{intensity}\n"

        self.serial.write(message.encode())

    def close(self):
        self.send_intensity(0)
        self.serial.close()
