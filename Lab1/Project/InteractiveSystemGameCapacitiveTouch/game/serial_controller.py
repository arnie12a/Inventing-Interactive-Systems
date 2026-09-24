import serial
import time


class SerialController:

    def __init__(
        self,
        port="/dev/cu.usbserial-0001",
        baud_rate=115200
    ):

        self.port = port
        self.baud_rate = baud_rate
        self.last_command = "NONE"

        try:

            self.arduino = serial.Serial(
                self.port,
                self.baud_rate,
                timeout=0.01
            )

            # Allow ESP32 to reset
            time.sleep(2)

            print("Connected to ESP32")

        except serial.SerialException as e:

            print("Could not connect to ESP32:")
            print(e)

            raise


    def get_command(self):

        valid_commands = [
            "LEFT",
            "RIGHT",
            "FORWARD",
            "DIAGONAL_LEFT",
            "DIAGONAL_RIGHT",
            "NONE"
        ]


        while self.arduino.in_waiting:

            try:

                line = self.arduino.readline().decode(
                    "utf-8",
                    errors="ignore"
                ).strip()


                if not line:
                    continue


                print("ESP32:", line)


                if line in valid_commands:
                    self.last_command = line


            except Exception as e:

                print("Serial read error:", e)


        return self.last_command


    def close(self):

        if self.arduino.is_open:
            self.arduino.close()