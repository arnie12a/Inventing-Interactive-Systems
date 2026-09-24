const int BUZZER_PIN = 5;

void setup() {
  // put your setup code here, to run once:

  pinMode(BUZZER_PIN, OUTPUT);
}

void loop() {
  // put your main code here, to run repeatedly:
  int frequency = 300;
  tone(BUZZER_PIN, frequency);
  delay(500);
  noTone(BUZZER_PIN);
  delay(500);
}
