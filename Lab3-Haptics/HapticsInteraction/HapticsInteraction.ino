// --------------------
// Motor connections
// --------------------
const int enA = 13;
const int in1 = 12;
const int in2 = 14;

// --------------------
// Joystick connections
// --------------------
const int joyX = 34;
const int joyY = 35;
const int joySW = 32;

void setup() {
  // Motor pins
  pinMode(enA, OUTPUT);
  pinMode(in1, OUTPUT);
  pinMode(in2, OUTPUT);

  // Joystick pins
  pinMode(joyX, INPUT);
  pinMode(joyY, INPUT);
  pinMode(joySW, INPUT_PULLUP);

  // Motor moves forward
  digitalWrite(in1, HIGH);
  digitalWrite(in2, LOW);

  // Start motor off
  analogWrite(enA, 0);

  Serial.begin(115200);
}

void loop() {

  // Read joystick Y axis
  // ESP32 analogRead gives approximately 0 - 4095
  int joystickValue = analogRead(joyY);

  // Convert joystick reading to motor PWM
  // 0 - 4095 becomes 0 - 255
  int motorSpeed = map(joystickValue, 0, 4095, 0, 255);

  // Set motor speed
  analogWrite(enA, motorSpeed);

  // Print values so we can see them in Serial Monitor
  Serial.print("Joystick: ");
  Serial.print(joystickValue);

  Serial.print("   Motor Speed: ");
  Serial.println(motorSpeed);

  delay(20);
}