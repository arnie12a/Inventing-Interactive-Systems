# ⚽ Pay Attention to Footy

---

## 📖 Project Overview

The idea of this application is make sure the user is paying attention to the soccer match. I am a huge soccer fan so I am always watching footy on the television. Growing up I was the same and on Sundays you would always see me on the couch watching Manchester United play. But my mom would always be bothering me making me do chores around the house and as a result I would miss out on goals because the volume would not reach the basement. So my idea of the app would evenutally be a wearable would tell the user when a team is about to score.

When you watch soccer matches on the television you can often hear the fans and commentator start to scream louder as the goal is about to happen so I thought this would be the perfect opportunity to use the acoustic sensing and haptic sensing together.

---

## 📂 Project Structure

```text
PayAttentionToFooty/
│
├── audio/
│   └── live_audio_haptics.py
│
├── haptics/
│   ├── esp32_motor/
│   │   └── esp32_motor.ino
│   │
│   └── test_motor.py
│
├── requirements.txt
└── README.md
```

---

## ⚙️ How the application works

1. Python listens to the video link that the user provides to the application
2. RMS is used to determine the the strength of the impulse
3. RMS is converted to decibels
4. Converts the decibels to motor intensity to buzz
5. Sends the motor intensity to the ESP32

---

## 🎥 Link to the demo

[https://youtu.be/_lGVYOmNm3I](https://youtu.be/_lGVYOmNm3I)

---

## 🚀 How to run the applicaiton

```bash
python3 audio/live_audio_haptics.py --url "https://www.youtube.com/watch?v=ydx1L0aDj_c"
```

---