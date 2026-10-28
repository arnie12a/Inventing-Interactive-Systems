
#define TRIG_PIN 32
#define ECHO_PIN 33

// Motor pins - tested and working
const int enA = 13;
const int in1 = 12;
const int in2 = 14;

// LED pins - replace with your actual wiring
const int ledPins[] = {18, 19, 21, 22};
const int NUM_LEDS = 4;

// Goal settings
const float GOAL_DISTANCE = 3.0;
const float RESET_DISTANCE = 5.0;

const unsigned long GOAL_DURATION = 5000;
const unsigned long FLASH_INTERVAL = 250;

// System state
bool goalActive = false;
bool waitingForReset = false;
bool ledsOn = false;

unsigned long goalStartTime = 0;
unsigned long lastFlashTime = 0;

void setLEDs(bool state) {
  for (int i = 0; i < NUM_LEDS; i++) {
    digitalWrite(ledPins[i], state ? HIGH : LOW);
  }
}

void motorOn() {
  digitalWrite(in1, HIGH);
  digitalWrite(in2, LOW);
  analogWrite(enA, 255);
}

void motorOff() {
  analogWrite(enA, 0);
  digitalWrite(in1, LOW);
  digitalWrite(in2, LOW);
}

float readDistance() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);

  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  unsigned long duration =
      pulseIn(ECHO_PIN, HIGH, 30000);

  if (duration == 0) {
    return -1;
  }

  return duration * 0.0343 / 2.0;
}

void setup() {
  Serial.begin(115200);

  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);

  pinMode(enA, OUTPUT);
  pinMode(in1, OUTPUT);
  pinMode(in2, OUTPUT);

  for (int i = 0; i < NUM_LEDS; i++) {
    pinMode(ledPins[i], OUTPUT);
  }

  motorOff();
  setLEDs(false);

  Serial.println("SOCCER GOAL SYSTEM READY!");
}

void loop() {
  unsigned long currentTime = millis();

  // Read distance
  float distance = readDistance();

  if (distance > 0) {
    Serial.print("Distance: ");
    Serial.print(distance);
    Serial.println(" cm");
  }

  // Detect goal
  if (!goalActive && !waitingForReset &&
      distance > 0 && distance <= GOAL_DISTANCE) {

    Serial.println("GOOOOOOOOOAL!");

    goalActive = true;
    goalStartTime = currentTime;
    lastFlashTime = currentTime;

    motorOn();

    ledsOn = true;
    setLEDs(true);
  }

  // Goal celebration
  if (goalActive) {

    // Stop after 5 seconds
    if (currentTime - goalStartTime >= GOAL_DURATION) {

      motorOff();
      setLEDs(false);

      ledsOn = false;
      goalActive = false;
      waitingForReset = true;

      Serial.println("Celebration finished!");
    }

    // Flash LEDs every 250 milliseconds
    else if (currentTime - lastFlashTime >= FLASH_INTERVAL) {

      ledsOn = !ledsOn;
      setLEDs(ledsOn);

      lastFlashTime = currentTime;
    }
  }

  // Reset after ball leaves
  if (waitingForReset &&
      distance > RESET_DISTANCE) {

    waitingForReset = false;
    Serial.println("RESET - READY FOR NEXT GOAL!");
  }

  delay(20);
}
