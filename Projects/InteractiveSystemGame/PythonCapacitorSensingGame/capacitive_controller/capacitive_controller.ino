// #define TOUCH_OFFSET 100

// const int TOUCH_LEFT   = 32;
// const int TOUCH_CENTER = 33;
// const int TOUCH_RIGHT  = 27;

// const int LED_LEFT   = 25;
// const int LED_CENTER = 26;
// const int LED_RIGHT  = 14;

// float baselineLeft = 0;
// float baselineCenter = 0;
// float baselineRight = 0;

// float thresholdLeft = 0;
// float thresholdCenter = 0;
// float thresholdRight = 0;

// void setup() {

//   Serial.begin(115200);

//   // LEDs
//   pinMode(LED_LEFT, OUTPUT);
//   pinMode(LED_CENTER, OUTPUT);
//   pinMode(LED_RIGHT, OUTPUT);

//   digitalWrite(LED_LEFT, LOW);
//   digitalWrite(LED_CENTER, LOW);
//   digitalWrite(LED_RIGHT, LOW);

//   delay(1000);

//   // -----------------------------
//   // CALIBRATION
//   // -----------------------------

//   Serial.println("CALIBRATING");

//   long totalLeft = 0;
//   long totalCenter = 0;
//   long totalRight = 0;

//   int samples = 0;

//   unsigned long startTime = millis();

//   // Calibrate for 5 seconds
//   while (millis() - startTime < 5000) {

//     totalLeft += touchRead(TOUCH_LEFT);
//     totalCenter += touchRead(TOUCH_CENTER);
//     totalRight += touchRead(TOUCH_RIGHT);

//     samples++;

//     delay(20);
//   }

//   // Calculate baseline

//   baselineLeft = (float)totalLeft / samples;
//   baselineCenter = (float)totalCenter / samples;
//   baselineRight = (float)totalRight / samples;

//   // Calculate thresholds

//   thresholdLeft = baselineLeft - TOUCH_OFFSET;
//   thresholdCenter = baselineCenter - TOUCH_OFFSET;
//   thresholdRight = baselineRight - TOUCH_OFFSET;

//   Serial.println("READY");

//   Serial.print("Left threshold: ");
//   Serial.println(thresholdLeft);

//   Serial.print("Center threshold: ");
//   Serial.println(thresholdCenter);

//   Serial.print("Right threshold: ");
//   Serial.println(thresholdRight);
// }

// void loop() {

//   // -----------------------------
//   // READ SENSORS
//   // -----------------------------

//   int leftValue = touchRead(TOUCH_LEFT);
//   int centerValue = touchRead(TOUCH_CENTER);
//   int rightValue = touchRead(TOUCH_RIGHT);

//   // -----------------------------
//   // DETERMINE TOUCH
//   // -----------------------------

//   bool leftTouched = leftValue < thresholdLeft;
//   bool centerTouched = centerValue < thresholdCenter;
//   bool rightTouched = rightValue < thresholdRight;

//   // -----------------------------
//   // TURN ALL LEDs OFF
//   // -----------------------------

//   digitalWrite(LED_LEFT, LOW);
//   digitalWrite(LED_CENTER, LOW);
//   digitalWrite(LED_RIGHT, LOW);

//   // -----------------------------
//   // MOVEMENT
//   // -----------------------------

//   // LEFT
//   if (leftTouched) {

//     digitalWrite(LED_LEFT, HIGH);

//     Serial.println("LEFT");
//   }

//   // CENTER
//   else if (centerTouched) {

//     digitalWrite(LED_CENTER, HIGH);

//     Serial.println("FORWARD");
//   }

//   // RIGHT
//   else if (rightTouched) {

//     digitalWrite(LED_RIGHT, HIGH);

//     Serial.println("RIGHT");
//   }

//   // NOTHING
//   else {

//     Serial.println("NONE");
//   }

//   delay(50);
// }
// =====================================================
// ESP32 CAPACITIVE GESTURE CONTROLLER
// =====================================================

// -----------------------------------------------------
// TOUCH SENSORS
// -----------------------------------------------------

const int TOUCH_LEFT   = 27; //32
const int TOUCH_CENTER = 33;
const int TOUCH_RIGHT  = 32; //27

// -----------------------------------------------------
// LEDS
// -----------------------------------------------------

const int LED_LEFT   = 25;
const int LED_CENTER = 26;
const int LED_RIGHT  = 14;

// -----------------------------------------------------
// TOUCH SETTINGS
// -----------------------------------------------------

#define TOUCH_OFFSET 100

// How long a diagonal gesture stays active
// after CENTER -> LEFT or CENTER -> RIGHT
const unsigned long DIAGONAL_TIME = 250;

// How often to send a command
const unsigned long SEND_INTERVAL = 30;

// -----------------------------------------------------
// CALIBRATION
// -----------------------------------------------------

float baselineLeft = 0;
float baselineCenter = 0;
float baselineRight = 0;

float thresholdLeft = 0;
float thresholdCenter = 0;
float thresholdRight = 0;


// -----------------------------------------------------
// SENSOR STATES
// -----------------------------------------------------

enum SensorPosition {
  POSITION_NONE,
  POSITION_LEFT,
  POSITION_CENTER,
  POSITION_RIGHT
};

SensorPosition previousPosition = POSITION_NONE;
SensorPosition currentPosition = POSITION_NONE;


// -----------------------------------------------------
// DIAGONAL GESTURE
// -----------------------------------------------------

String diagonalCommand = "NONE";

unsigned long diagonalStartTime = 0;


// -----------------------------------------------------
// SERIAL TIMING
// -----------------------------------------------------

unsigned long lastSendTime = 0;


// =====================================================
// FUNCTION: READ POSITION
// =====================================================

SensorPosition readPosition() {

  int leftValue = touchRead(TOUCH_LEFT);
  int centerValue = touchRead(TOUCH_CENTER);
  int rightValue = touchRead(TOUCH_RIGHT);

  bool leftTouched =
    leftValue < thresholdLeft;

  bool centerTouched =
    centerValue < thresholdCenter;

  bool rightTouched =
    rightValue < thresholdRight;

  // -----------------------------------------------
  // Find strongest touch
  // -----------------------------------------------

  float leftStrength =
    baselineLeft - leftValue;

  float centerStrength =
    baselineCenter - centerValue;

  float rightStrength =
    baselineRight - rightValue;


  // -----------------------------------------------
  // Determine which sensor is strongest
  // -----------------------------------------------

  if (!leftTouched &&
      !centerTouched &&
      !rightTouched) {

    return POSITION_NONE;
  }


  if (leftTouched &&
      leftStrength >= centerStrength &&
      leftStrength >= rightStrength) {

    return POSITION_LEFT;
  }


  if (rightTouched &&
      rightStrength >= leftStrength &&
      rightStrength >= centerStrength) {

    return POSITION_RIGHT;
  }


  if (centerTouched) {

    return POSITION_CENTER;
  }


  return POSITION_NONE;
}


// =====================================================
// FUNCTION: UPDATE LEDS
// =====================================================

void updateLEDs(SensorPosition position) {

  digitalWrite(LED_LEFT, LOW);
  digitalWrite(LED_CENTER, LOW);
  digitalWrite(LED_RIGHT, LOW);


  // Normal slider position
  if (position == POSITION_LEFT) {

    digitalWrite(LED_LEFT, HIGH);

  }

  else if (position == POSITION_CENTER) {

    digitalWrite(LED_CENTER, HIGH);

  }

  else if (position == POSITION_RIGHT) {

    digitalWrite(LED_RIGHT, HIGH);

  }


  // During a diagonal gesture
  if (diagonalCommand == "DIAGONAL_LEFT") {

    digitalWrite(LED_CENTER, HIGH);
    digitalWrite(LED_LEFT, HIGH);

  }

  else if (diagonalCommand == "DIAGONAL_RIGHT") {

    digitalWrite(LED_CENTER, HIGH);
    digitalWrite(LED_RIGHT, HIGH);

  }
}


// =====================================================
// FUNCTION: GET COMMAND
// =====================================================

String getCommand() {

  // -----------------------------------------------
  // Check diagonal gesture timer
  // -----------------------------------------------

  if (diagonalCommand != "NONE") {

    if (millis() - diagonalStartTime
        < DIAGONAL_TIME) {

      return diagonalCommand;

    }

    else {

      diagonalCommand = "NONE";
    }
  }


  // -----------------------------------------------
  // Normal slider movement
  // -----------------------------------------------

  if (currentPosition == POSITION_LEFT) {

    return "LEFT";
  }

  if (currentPosition == POSITION_CENTER) {

    return "FORWARD";
  }

  if (currentPosition == POSITION_RIGHT) {

    return "RIGHT";
  }

  return "NONE";
}


// =====================================================
// SETUP
// =====================================================

void setup() {

  Serial.begin(115200);


  // ---------------------------------------------------
  // LEDs
  // ---------------------------------------------------

  pinMode(LED_LEFT, OUTPUT);
  pinMode(LED_CENTER, OUTPUT);
  pinMode(LED_RIGHT, OUTPUT);

  digitalWrite(LED_LEFT, LOW);
  digitalWrite(LED_CENTER, LOW);
  digitalWrite(LED_RIGHT, LOW);


  // ---------------------------------------------------
  // Give ESP32 time to start
  // ---------------------------------------------------

  delay(1000);


  // ---------------------------------------------------
  // CALIBRATION
  // ---------------------------------------------------

  Serial.println();
  Serial.println("==============================");
  Serial.println("Starting calibration...");
  Serial.println("DO NOT TOUCH THE SENSORS");
  Serial.println("==============================");


  long totalLeft = 0;
  long totalCenter = 0;
  long totalRight = 0;

  int samples = 0;

  unsigned long startTime = millis();


  while (millis() - startTime < 2000) {

    totalLeft += touchRead(TOUCH_LEFT);
    totalCenter += touchRead(TOUCH_CENTER);
    totalRight += touchRead(TOUCH_RIGHT);

    samples++;

    delay(10);
  }


  baselineLeft =
    (float) totalLeft / samples;

  baselineCenter =
    (float) totalCenter / samples;

  baselineRight =
    (float) totalRight / samples;


  // ---------------------------------------------------
  // Create thresholds
  // ---------------------------------------------------

  thresholdLeft =
    baselineLeft - TOUCH_OFFSET;

  thresholdCenter =
    baselineCenter - TOUCH_OFFSET;

  thresholdRight =
    baselineRight - TOUCH_OFFSET;


  // ---------------------------------------------------
  // Print calibration values
  // ---------------------------------------------------

  Serial.println();
  Serial.println("Calibration complete.");

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
  Serial.println("==============================");
  Serial.println("Gesture controller ready");
  Serial.println("==============================");
}


// =====================================================
// LOOP
// =====================================================

void loop() {

  // ---------------------------------------------------
  // Determine current slider position
  // ---------------------------------------------------

  currentPosition = readPosition();


  // ---------------------------------------------------
  // Detect CENTER -> LEFT
  // ---------------------------------------------------

  if (previousPosition == POSITION_CENTER &&
      currentPosition == POSITION_LEFT) {

    diagonalCommand = "DIAGONAL_LEFT";

    diagonalStartTime = millis();

    Serial.println("DIAGONAL_LEFT");
  }


  // ---------------------------------------------------
  // Detect CENTER -> RIGHT
  // ---------------------------------------------------

  if (previousPosition == POSITION_CENTER &&
      currentPosition == POSITION_RIGHT) {

    diagonalCommand = "DIAGONAL_RIGHT";

    diagonalStartTime = millis();

    Serial.println("DIAGONAL_RIGHT");
  }


  // ---------------------------------------------------
  // Update previous position
  // ---------------------------------------------------

  previousPosition = currentPosition;


  // ---------------------------------------------------
  // Update LEDs
  // ---------------------------------------------------

  updateLEDs(currentPosition);


  // ---------------------------------------------------
  // Send current command periodically
  // ---------------------------------------------------

  if (millis() - lastSendTime >= SEND_INTERVAL) {

    String command = getCommand();

    Serial.println(command);

    lastSendTime = millis();
  }


  delay(5);
}