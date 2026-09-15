#define TOUCH_OFFSET 100

const int TOUCH_LEFT   = 32;
const int TOUCH_CENTER = 33;
const int TOUCH_RIGHT  = 27;

const int LED_LEFT   = 25;
const int LED_CENTER = 26;
const int LED_RIGHT  = 14;

float baselineLeft = 0;
float baselineCenter = 0;
float baselineRight = 0;

float thresholdLeft = 0;
float thresholdCenter = 0;
float thresholdRight = 0;

void setup() {

  Serial.begin(115200);

  // LEDs
  pinMode(LED_LEFT, OUTPUT);
  pinMode(LED_CENTER, OUTPUT);
  pinMode(LED_RIGHT, OUTPUT);

  digitalWrite(LED_LEFT, LOW);
  digitalWrite(LED_CENTER, LOW);
  digitalWrite(LED_RIGHT, LOW);

  delay(1000);

  // -----------------------------
  // CALIBRATION
  // -----------------------------

  Serial.println("CALIBRATING");

  long totalLeft = 0;
  long totalCenter = 0;
  long totalRight = 0;

  int samples = 0;

  unsigned long startTime = millis();

  // Calibrate for 5 seconds
  while (millis() - startTime < 5000) {

    totalLeft += touchRead(TOUCH_LEFT);
    totalCenter += touchRead(TOUCH_CENTER);
    totalRight += touchRead(TOUCH_RIGHT);

    samples++;

    delay(20);
  }

  // Calculate baseline

  baselineLeft = (float)totalLeft / samples;
  baselineCenter = (float)totalCenter / samples;
  baselineRight = (float)totalRight / samples;

  // Calculate thresholds

  thresholdLeft = baselineLeft - TOUCH_OFFSET;
  thresholdCenter = baselineCenter - TOUCH_OFFSET;
  thresholdRight = baselineRight - TOUCH_OFFSET;

  Serial.println("READY");

  Serial.print("Left threshold: ");
  Serial.println(thresholdLeft);

  Serial.print("Center threshold: ");
  Serial.println(thresholdCenter);

  Serial.print("Right threshold: ");
  Serial.println(thresholdRight);
}

void loop() {

  // -----------------------------
  // READ SENSORS
  // -----------------------------

  int leftValue = touchRead(TOUCH_LEFT);
  int centerValue = touchRead(TOUCH_CENTER);
  int rightValue = touchRead(TOUCH_RIGHT);

  // -----------------------------
  // DETERMINE TOUCH
  // -----------------------------

  bool leftTouched = leftValue < thresholdLeft;
  bool centerTouched = centerValue < thresholdCenter;
  bool rightTouched = rightValue < thresholdRight;

  // -----------------------------
  // TURN ALL LEDs OFF
  // -----------------------------

  digitalWrite(LED_LEFT, LOW);
  digitalWrite(LED_CENTER, LOW);
  digitalWrite(LED_RIGHT, LOW);

  // -----------------------------
  // MOVEMENT
  // -----------------------------

  // LEFT
  if (leftTouched) {

    digitalWrite(LED_LEFT, HIGH);

    Serial.println("LEFT");
  }

  // CENTER
  else if (centerTouched) {

    digitalWrite(LED_CENTER, HIGH);

    Serial.println("FORWARD");
  }

  // RIGHT
  else if (rightTouched) {

    digitalWrite(LED_RIGHT, HIGH);

    Serial.println("RIGHT");
  }

  // NOTHING
  else {

    Serial.println("NONE");
  }

  delay(50);
}