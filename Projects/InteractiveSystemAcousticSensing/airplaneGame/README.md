# Acoustic Sensing Airplane Game

### Link to the game

[Acoustic Sensing Lab Video](https://youtu.be/r7rkrjZ47EI?si=byxMDSr5rdERw78Y)

### Overview of the game

An interactive game that uses real-time acoustic sensing to detect clap gesttures through a microphone. The application of the game is using hte FFT enhanced from part 2 of the lab to analyze acousitic signal to detect the input gesture of clapping.

The game regonizes both single claps and double claps.

#### Aspsects of the game

- During the power-up phase, double claps generate power
- A single clap is used to launch the airplane at the indicated angle
- The intensity of the clap affects the amount of power generated for the airplane from launch
- After launch, the airplane follows a simulated trajectory under gravity
- The user can implement a boost by double clapping once once the airplane has been launched
- Flight records are recorded and compared to the leaderboard

---

## Understanding the Interactive System

The microphone is configured with:

```text
SAMPLE_RATE = 48_000 Hz
BLOCK_SIZE = 1024
```

which means that the the microphone captures 48,000 samples every single second. Then the program processes the incoming signal in blocks of 1024 samples.

FFT is used to convert the signal from the time domain to the frequency domain which is then utilized to detect the clap.

#### Detecting a clap

1. The sound must contain enough overall energy
2. A sufficient percentage fo the specral energy must occur within the frequency range associated with the clap

---

#### Measuring Clap Intensity

The game estimates how strong the clap was.

Both RMS amplitude and peak amplitude are measured. RMS measures the overall acoustic amplitute and the peak is the largest instantaneous amplitude.

The measurements are normalized into a range from around 0 to 1.

```text
Weak clap -> 0.2
Medium clap -> 0.5
Strong clap -> 0.85
```

The clap-strength measurement is used by the game so that a stronger acoustic input has a larger affect on the game compared to a weaker input.

If a double clap is detected, then a times two factor is enacted on the power_gain.

---

#### Single Clap vs. Double clap

The FFT is used to identify each individual clap. To detect a double clap the program still uses the FFT-based detector but there is a time stamp that is assoicated with every detected clap. If the claps are within 0.5 seconds of one another then we can determine that this is a double clap.

After a clap is detected, additional detections are ignored for approximately 120 milliseconds. The reason is for a single acoustic impulse from being interpreted a multiple gestures at once.

---

### The game itself

#### Power-Up Phase

double clapping and the intensity of the claps determines the power the airplane is going to be launched with

#### Launch Phase

The airplane continuously changes its launch angle between 0 and 90 degrees and a single clap selects the angle in which the airplane will be launched.

#### Mid-Flight Boost

After launch, the airplane can experience a upward boost by a double clap.

---

### AI Usage
AI was used for the development of the application. clap_detector.py was implemented on top of the fft_bin python script given to us from the lab. The layout of the game was created and drawn out by myself but ht actual code from the game is generated through many iterations of ChatGPT. 

### Application StructureairplaneGame/

```text
airplaneGame/
|
|-- main.py
|-- clap_detector.py
|-- game.py
|-- airplane.py
|-- requirements.txt
`-- flight_results.csv
```

---

### Running the game

```bash
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```