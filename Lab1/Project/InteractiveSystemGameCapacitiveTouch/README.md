# ESP32 Capacitive Sensor Obstacle Course

[Youtube Video for Capacitive Sensor Lab](https://youtu.be/dD5uCymqWyc)


## Overview

This project uses capacitive touch sensors connected to an ESP32 to play a python coded game on a computer. Instead of using the arrows on the keyboard to move the player around, the user can touch or swipe no the controller to move an object through an obstacle course to the finish line. 

The ESP32 detects what the user wants to do with the three capacitive touch sensors and sends movement commands to the Python applicatin through serial communication which we were able to see in the arduino console thorugh the serial monitor. The Python applciation ingests that serial data from the commands the player does and uses Pygame to display the game.

The goal of the game is for the user to move through the obstacle course as fast as they can. At the end of the game the users name, date they played, and time is recorded so we can track which user is the fastest through the obstacle course. 

---

## Controls

The system uses three capacitive touch sensors: **Left**, **Center**, and **Right**.

| Input                | Command          | Player Movement                   |
| -------------------- | ---------------- | --------------------------------- |
| Left sensor          | `LEFT`           | Move left                         |
| Right sensor         | `RIGHT`          | Move right                        |
| Center sensor        | `FORWARD`        | Move forward                      |
| Center → Left swipe  | `DIAGONAL_LEFT`  | Move diagonally forward and left  |
| Center → Right swipe | `DIAGONAL_RIGHT` | Move diagonally forward and right |
| No touch             | `NONE`           | No movement                       |

The ESP32 is able to comprehend individual touches of the capacitive sensors along with swipes as well. 

---

## Project Structure

```text
PythonCapacitorSensingGame/
│
└── game/
    └── main.py
    └── serial_controller.py
    └── obstacles.py
    └── score.csv
└── capacitive_controller/
    └── capacitive_controller.ino
```

### `capacitive_controller.ino`

This program runs on the ESP32. It reads the values from the three capacitive touch sensors. It takes five seconds of calibration so a baseline is determined for each of the three sensors. The code detects individual detection of sensors and also center-to-left and center-to-right swipe gestures. There are three LEDs that are used for testing purposes to test if the individual capacitive sensor and swipe gestures are detecting proiperly. Finally, the program sends movement commands over the serial connection for the python program to take in. 


The possible serial commands are:

```text
NONE
LEFT
RIGHT
FORWARD
DIAGONAL_LEFT
DIAGONAL_RIGHT
```

### `serial_controller.py`

manages communication between the ESP32 and the Python application. It validates the incoming commands coming from the ESP32. It also provides the most recent command to the game that the user on the screen then performs. 


### `obstacles.py`

This file contains the obstacle course. There are three different courses that get selected at random when the user starts the game. 


### `main.py`

The python file that actually runs the game. It reads the commands passed in from the ESP32 and serial_controller and actaully does the command progressing the user towards the finish line. The game is entirely handled in this file. 


### `scores.csv`

Stores the scores for each user's attempt at the obstacle course. 
---

# How the Application Works
The overall communication flow is:

```text
Capacitive Touch Sensors
          ↓
        ESP32
          ↓
 serial_controller.py
          ↓
       main.py
          ↓
       Pygame
          ↓
   Player Movement
```
The ESP32 tracks the Capacitive Touch Sensor that converts the touch to commands that is either LEFT, RIGHT, FORWARD, DIAGONAL LEFT, DIAGONAL RIGHT, or NONE which gets passed to the serial_controller. Once the command is validated it gets passed into the actual game python script that performs the players movement on the computer screen. 


# How to run the Application

To run this application you have to upload the code to the ESP32 through the arduino IDE. Once the application is running on the ESP32 you go to the python code and run the script 

```
python3 main.py
```

which builds out the pygame user interface that users can then play the obstacle course by following the directions that are presented to them on the screen. 




# Use of Artificial Intelligence

ChatGPT was used to : 

* Brainstorm the organization between the ESP32, serial_controller, and the actual python application
* Template code for main.py, obstacles.py, serial_controller, and capacitive_controller 

