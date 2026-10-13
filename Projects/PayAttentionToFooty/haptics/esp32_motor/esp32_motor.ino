
// PayAttentionToFooty - Acoustic Haptics
// ESP32 motor driver connections

const int enA = 13;
const int in1 = 12;
const int in2 = 14;

const int PWM_FREQ = 5000;
const int PWM_RESOLUTION = 8;

// Start with a conservative motor limit
const int MAX_PWM = 150;

// Stop motor if Python stops sending commands
const unsigned long TIMEOUT_MS = 500;
unsigned long lastCommand = 0;

void stopMotor() {
    ledcWrite(enA, 0);
    digitalWrite(in1, LOW);
    digitalWrite(in2, LOW);
}

void setup() {
    Serial.begin(115200);
    Serial.setTimeout(50);

    pinMode(in1, OUTPUT);
    pinMode(in2, OUTPUT);

    digitalWrite(in1, LOW);
    digitalWrite(in2, LOW);

    // PWM on the motor driver's enable pin
    if (!ledcAttach(enA, PWM_FREQ, PWM_RESOLUTION)) {
        Serial.println("PWM SETUP FAILED");
        return;
    }

    stopMotor();

    lastCommand = millis();

    Serial.println("ESP32 HAPTICS READY");
}

void loop() {
    if (Serial.available() > 0) {

        String input = Serial.readStringUntil('\n');
        input.trim();

        bool valid = input.length() > 0;

        for (int i = 0; i < input.length(); i++) {
            if (!isDigit(input[i])) {
                valid = false;
                break;
            }
        }

        if (valid) {
            int pwm = constrain(
                input.toInt(),
                0,
                MAX_PWM
            );

            if (pwm > 0) {
                // Keep motor running forward
                digitalWrite(in1, HIGH);
                digitalWrite(in2, LOW);
                ledcWrite(enA, pwm);
            } else {
                stopMotor();
            }

            lastCommand = millis();

            Serial.print("RECEIVED PWM: ");
            Serial.println(pwm);
        }
    }

    // Safety timeout
    if (millis() - lastCommand > TIMEOUT_MS) {
        stopMotor();
    }
}
