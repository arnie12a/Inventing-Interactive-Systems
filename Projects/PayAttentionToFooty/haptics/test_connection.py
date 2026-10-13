
import serial
import time

PORT = "/dev/cu.usbserial-0001"
BAUD = 115200

try:
    print(f"Connecting to ESP32 on {PORT}...")

    esp32 = serial.Serial(
        PORT,
        BAUD,
        timeout=1,
        write_timeout=1
    )

    time.sleep(2)

    print("Serial port opened successfully!")

    # Send a test command
    esp32.write(b"80\n")
    esp32.flush()

    print("Sent PWM value: 80")

    # Check for responses
    time.sleep(0.2)

    while esp32.in_waiting:
        response = esp32.readline()
        print("ESP32 response:", response.decode(
            errors="replace"
        ).strip())

    esp32.write(b"0\n")
    esp32.close()

except serial.SerialException as error:
    print(f"Serial connection failed: {error}")
