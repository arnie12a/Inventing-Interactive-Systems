#define TOUCH_OFFSET 50

// Touch sensor pins
const int TOUCH_LEFT   = 32;
const int TOUCH_CENTER = 33;
const int TOUCH_RIGHT  = 27;

// LED pins
const int LED_LEFT   = 25;
const int LED_CENTER = 26;
const int LED_RIGHT  = 14;

// Baselines
float baselineLeft = 0;
float baselineCenter = 0;
float baselineRight = 0;

// Thresholds
float thresholdLeft = 0;
float thresholdCenter = 0;
float thresholdRight = 0;

// Used to remember the previous sensor position
int previousPosition = -1;

// Used to remember whether a gesture has started
int gestureStart = -1;

// Used to make sure the gesture progresses in order
int lastGesturePosition = -1;

void setup() {
  Serial.begin(115200);

  // LEDs are outputs
  pinMode(LED_LEFT, OUTPUT);
  pinMode(LED_CENTER, OUTPUT);
  pinMode(LED_RIGHT, OUTPUT);

  // Start with LEDs off
  digitalWrite(LED_LEFT, LOW);
  digitalWrite(LED_CENTER, LOW);
  digitalWrite(LED_RIGHT, LOW);

  delay(1000);

  // -------------------------
  // CALIBRATION
  // -------------------------

  Serial.println("Starting calibration...");
  Serial.println("Do NOT touch the sensors.");

  long totalLeft = 0;
  long totalCenter = 0;
  long totalRight = 0;

  int samples = 0;

  unsigned long startTime = millis();

  // Collect readings for 5 seconds
  while (millis() - startTime < 5000) {

    totalLeft += touchRead(TOUCH_LEFT);
    totalCenter += touchRead(TOUCH_CENTER);
    totalRight += touchRead(TOUCH_RIGHT);

    samples++;

    delay(20);
  }

  // Calculate baselines
  baselineLeft = (float)totalLeft / samples;
  baselineCenter = (float)totalCenter / samples;
  baselineRight = (float)totalRight / samples;

  // Calculate thresholds
  thresholdLeft = baselineLeft - TOUCH_OFFSET;
  thresholdCenter = baselineCenter - TOUCH_OFFSET;
  thresholdRight = baselineRight - TOUCH_OFFSET;

  Serial.println();
  Serial.println("Calibration complete!");

  Serial.print("Left baseline: ");
  Serial.println(baselineLeft);

  Serial.print("Center baseline: ");
  Serial.println(baselineCenter);

  Serial.print("Right baseline: ");
  Serial.println(baselineRight);

  Serial.println();

  Serial.print("Left threshold: ");
  Serial.println(thresholdLeft);

  Serial.print("Center threshold: ");
  Serial.println(thresholdCenter);

  Serial.print("Right threshold: ");
  Serial.println(thresholdRight);

  Serial.println();
  Serial.println("Gesture recognition ready!");
}


// Returns:
// 0 = left
// 1 = center
// 2 = right
// -1 = nothing
int getTouchPosition(float leftAmount, float centerAmount, float rightAmount,
                     bool leftTouched, bool centerTouched, bool rightTouched) {

  // Nothing touched
  if (!leftTouched && !centerTouched && !rightTouched) {
    return -1;
  }

  // Find strongest sensor
  if (leftAmount >= centerAmount && leftAmount >= rightAmount) {
    return 0;
  }

  if (centerAmount >= leftAmount && centerAmount >= rightAmount) {
    return 1;
  }

  return 2;
}


void loop() {

  // -------------------------
  // READ SENSORS
  // -------------------------

  int leftValue = touchRead(TOUCH_LEFT);
  int centerValue = touchRead(TOUCH_CENTER);
  int rightValue = touchRead(TOUCH_RIGHT);

  float leftAmount = baselineLeft - leftValue;
  float centerAmount = baselineCenter - centerValue;
  float rightAmount = baselineRight - rightValue;

  if (leftAmount < 0) leftAmount = 0;
  if (centerAmount < 0) centerAmount = 0;
  if (rightAmount < 0) rightAmount = 0;


  // -------------------------
  // IS EACH SENSOR TOUCHED?
  // -------------------------

  bool leftTouched = leftValue < thresholdLeft;
  bool centerTouched = centerValue < thresholdCenter;
  bool rightTouched = rightValue < thresholdRight;


  // -------------------------
  // CONTROL LEDs
  // -------------------------

  digitalWrite(LED_LEFT, leftTouched ? HIGH : LOW);
  digitalWrite(LED_CENTER, centerTouched ? HIGH : LOW);
  digitalWrite(LED_RIGHT, rightTouched ? HIGH : LOW);


  // -------------------------
  // DETERMINE STRONGEST POSITION
  // -------------------------

  int currentPosition = getTouchPosition(
    leftAmount,
    centerAmount,
    rightAmount,
    leftTouched,
    centerTouched,
    rightTouched
  );


  // Default: no completed swipe
  String gesture = "NO_SWIPE";


  // -------------------------
  // START GESTURE
  // -------------------------

  if (gestureStart == -1 && currentPosition != -1) {

    // Only start swipe from LEFT or RIGHT
    if (currentPosition == 0 || currentPosition == 2) {
      gestureStart = currentPosition;
      lastGesturePosition = currentPosition;
    }
  }


  // -------------------------
  // GESTURE RECOGNITION
  // -------------------------

  if (currentPosition != -1 &&
      currentPosition != lastGesturePosition) {


    // LEFT -> CENTER -> RIGHT
    if (gestureStart == 0) {

      // Left -> Center
      if (lastGesturePosition == 0 &&
          currentPosition == 1) {

        lastGesturePosition = 1;
      }

      // Center -> Right
      else if (lastGesturePosition == 1 &&
               currentPosition == 2) {

        gesture = "RIGHT_SWIPE";

        gestureStart = -1;
        lastGesturePosition = -1;
      }
    }


    // RIGHT -> CENTER -> LEFT
    else if (gestureStart == 2) {

      // Right -> Center
      if (lastGesturePosition == 2 &&
          currentPosition == 1) {

        lastGesturePosition = 1;
      }

      // Center -> Left
      else if (lastGesturePosition == 1 &&
               currentPosition == 0) {

        gesture = "LEFT_SWIPE";

        gestureStart = -1;
        lastGesturePosition = -1;
      }
    }
  }


  // -------------------------
  // PRINT DATA
  // -------------------------

  Serial.print(leftTouched ? 1 : 0);
  Serial.print(" ");

  Serial.print(centerTouched ? 1 : 0);
  Serial.print(" ");

  Serial.print(rightTouched ? 1 : 0);
  Serial.print(" ");

  Serial.println(gesture);


  delay(40);
}