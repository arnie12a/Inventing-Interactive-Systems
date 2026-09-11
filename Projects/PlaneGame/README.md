# Capacitive Airplane Landing Game

An interactive airplane landing game controlled using
three capacitive touch sensors connected to an ESP32.

## Controls

Left-to-right swipe:
Move airplane right

Right-to-left swipe:
Move airplane left

## Hardware

- ESP32
- 3 capacitive touch pads
- 3 LEDs

## Software

- Arduino
- Python
- Pygame
- PySerial

## Running the game

1. Upload capacitive_controller.ino to ESP32
2. Connect ESP32 over USB
3. Install Python dependencies
4. Run:

   python game/main.py