
import serial
import time

PORT = "/dev/cu.usbserial-0001"
BAUD = 115200

print("Connecting to ESP32...")

esp32 = serial.Serial(
    PORT,
    BAUD,
    timeout=0.1,
    write_timeout=1
)

time.sleep(2)

print("Connected!")

try:
    # Test different motor intensities
    intensities = [0, 50, 80, 110, 150, 80, 0]

    for pwm in intensities:

        print(f"\nTesting PWM: {pwm}")

        start = time.monotonic()

        while time.monotonic() - start < 2:

            esp32.write(f"{pwm}\n".encode())
            esp32.flush()

            time.sleep(0.1)

            while esp32.in_waiting:
                response = esp32.readline().decode(
                    errors="replace"
                ).strip()

                if response:
                    print("ESP32:", response)

finally:
    esp32.write(b"0\n")
    esp32.close()

print("\nMotor test completed.")
