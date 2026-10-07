const int TOUCH_PIN = 32;
const int LED_PIN = 27;
int counter = 0;

void setup() {
  // put your setup code here, to run once:
  pinMode(LED_PIN, OUTPUT);
  pinMode(TOUCH_PIN, INPUT);
  Serial.begin(115200);
}

void loop() {
  // put your main code here, to run repeatedly:
  Serial.println(counter);
  counter+=1;
  int sensedValue = touchRead(TOUCH_PIN);
  delay(10);
}
