// Motor connections
const int enA = 13;
const int in1 = 12;
const int in2 = 14;

void setup() {
  // Set all the pins as outputs
  pinMode(enA, OUTPUT);
  pinMode(in1, OUTPUT);
  pinMode(in2, OUTPUT);

  // Turn off the motor to start with
  analogWrite(enA, 0);
  digitalWrite(in1, LOW);
  digitalWrite(in2, LOW);

  Serial.begin(115200);
}

void loop() {
  // Set motor direction
  forward();

  // Ramp from 0 -> 255 over 1 second
  rampUp(1000);

  // Run at full speed for 0.5 seconds
  analogWrite(enA, 255);
  delay(500);

  // Ramp from 255 -> 0 over 0.6 seconds
  rampDown(600);

  // Remain off for 0.5 seconds
  stop();
  delay(500);
}

void forward() {
  digitalWrite(in1, HIGH);
  digitalWrite(in2, LOW);
}

void backward() {
  digitalWrite(in1, LOW);
  digitalWrite(in2, HIGH);
}

void stop() {
  analogWrite(enA, 0);
  digitalWrite(in1, LOW);
  digitalWrite(in2, LOW);
}

// Ramp motor from 0 to 255
void rampUp(int duration) {
  const int steps = 255;
  int stepDelay = duration / steps;

  for (int pwm = 0; pwm <= 255; pwm++) {
    analogWrite(enA, pwm);
    delay(stepDelay);
  }
}

// Ramp motor from 255 to 0
void rampDown(int duration) {
  const int steps = 255;
  int stepDelay = duration / steps;

  for (int pwm = 255; pwm >= 0; pwm--) {
    analogWrite(enA, pwm);
    delay(stepDelay);
  }
}