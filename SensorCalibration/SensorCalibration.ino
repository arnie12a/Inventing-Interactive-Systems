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

  // Set LED pins as outputs
  pinMode(LED_LEFT, OUTPUT);
  pinMode(LED_CENTER, OUTPUT);
  pinMode(LED_RIGHT, OUTPUT);

  // Make sure all LEDs start OFF
  digitalWrite(LED_LEFT, LOW);
  digitalWrite(LED_CENTER, LOW);
  digitalWrite(LED_RIGHT, LOW);

  delay(1000);

  Serial.println("Starting calibration...");
  Serial.println("Do NOT touch the sensors.");

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

  Serial.println("Calibration complete!");

  Serial.print("Left baseline: ");
  Serial.println(baselineLeft);

  Serial.print("Center baseline: ");
  Serial.println(baselineCenter);

  Serial.print("Right baseline: ");
  Serial.println(baselineRight);
}

void loop() {

  int leftValue = touchRead(TOUCH_LEFT);
  int centerValue = touchRead(TOUCH_CENTER);
  int rightValue = touchRead(TOUCH_RIGHT);

  // Calculate touch strength
  float leftAmount = baselineLeft - leftValue;
  float centerAmount = baselineCenter - centerValue;
  float rightAmount = baselineRight - rightValue;

  // Prevent negative values
  if (leftAmount < 0) leftAmount = 0;
  if (centerAmount < 0) centerAmount = 0;
  if (rightAmount < 0) rightAmount = 0;

  // Turn ALL LEDs off first
  digitalWrite(LED_LEFT, LOW);
  digitalWrite(LED_CENTER, LOW);
  digitalWrite(LED_RIGHT, LOW);

  // Determine which section is touched
  if (leftValue < thresholdLeft &&
      leftAmount >= centerAmount &&
      leftAmount >= rightAmount) {

    Serial.println("SLIDER: LEFT");
    digitalWrite(LED_LEFT, HIGH);

  } else if (centerValue < thresholdCenter &&
             centerAmount >= leftAmount &&
             centerAmount >= rightAmount) {

    Serial.println("SLIDER: CENTER");
    digitalWrite(LED_CENTER, HIGH);

  } else if (rightValue < thresholdRight &&
             rightAmount >= leftAmount &&
             rightAmount >= centerAmount) {

    Serial.println("SLIDER: RIGHT");
    digitalWrite(LED_RIGHT, HIGH);

  } else {

    Serial.println("SLIDER: NONE");
  }

  delay(50);
}