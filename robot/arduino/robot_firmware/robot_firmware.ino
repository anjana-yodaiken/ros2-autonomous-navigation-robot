#include <Wire.h>
#include <MPU6050.h>

// --- Pin definitions ---
#define M1_DIR  10
#define M1_PWM  11
#define M2_DIR  12
#define M2_PWM  13

#define M1_ENC_A  3
#define M1_ENC_B  2
#define M2_ENC_A  18
#define M2_ENC_B  19

#define MAX_SPEED_MPS 0.58
#define MAX_PWM 60//138  

// --- Encoder tick counters (updated in ISRs) ---
volatile long m1_ticks = 0;
volatile long m2_ticks = 0;

MPU6050 mpu;
char input_buf[32];
int input_len = 0;
unsigned long lastCmdTime = 0;

void setup() {
    Serial.begin(115200);

    pinMode(M1_DIR, OUTPUT); digitalWrite(M1_DIR, LOW);
    pinMode(M1_PWM, OUTPUT); digitalWrite(M1_PWM, LOW);
    pinMode(M2_DIR, OUTPUT); digitalWrite(M2_DIR, LOW);
    pinMode(M2_PWM, OUTPUT); digitalWrite(M2_PWM, LOW);

    pinMode(M1_ENC_A, INPUT_PULLUP);
    pinMode(M1_ENC_B, INPUT_PULLUP);
    pinMode(M2_ENC_A, INPUT_PULLUP);
    pinMode(M2_ENC_B, INPUT_PULLUP);

    attachInterrupt(digitalPinToInterrupt(M1_ENC_A), m1_encoder_isr, CHANGE);
    attachInterrupt(digitalPinToInterrupt(M2_ENC_A), m2_encoder_isr, CHANGE);

    Wire.begin();
    mpu.initialize();
}

void loop() {
    if (millis() - lastCmdTime > 500) {
        set_motor(M1_DIR, M1_PWM, 0);
        set_motor(M2_DIR, M2_PWM, 0);
    }

    while (Serial.available()) {
        char c = Serial.read();
        if (c == '\n') {
            input_buf[input_len] = '\0';
            parseCommand(input_buf);
            input_len = 0;
        } else if (input_len < 31) {
            input_buf[input_len++] = c;
        }
    }

  static unsigned long lastImu = 0;
  if (millis() - lastImu > 20) {
    int16_t ax, ay, az, gx, gy, gz;
    mpu.getMotion6(&ax, &ay, &az, &gx, &gy, &gz);

    Serial.print("IMU ");
    Serial.print(ax / 16384.0 * 9.81, 4); Serial.print(" ");
    Serial.print(ay / 16384.0 * 9.81, 4); Serial.print(" ");
    Serial.print(az / 16384.0 * 9.81, 4); Serial.print(" ");
    Serial.print(gx / 131.0 * 0.017453, 4); Serial.print(" ");
    Serial.print(gy / 131.0 * 0.017453, 4); Serial.print(" ");
    Serial.println(gz / 131.0 * 0.017453, 4);
    lastImu = millis();
  }

  static unsigned long lastEnc = 0;
  if (millis() - lastEnc > 50) {
        long t1, t2;

        noInterrupts();
        t1 = m1_ticks;
        t2 = m2_ticks;
        interrupts();
        
        Serial.print("ENC ");
        Serial.print(t1);
        Serial.print(" ");
        Serial.println(t2);
        lastEnc = millis();
    }
}

void parseCommand(char* cmd) {
  if (strncmp(cmd, "VEL", 3) == 0) {
    char* tok1 = strtok(cmd + 4, " ");
    char* tok2 = strtok(NULL, " ");
    if (tok1 == NULL || tok2 == NULL) return;
    set_motor(M1_DIR, M1_PWM, atof(tok1));
    set_motor(M2_DIR, M2_PWM, atof(tok2));
    lastCmdTime = millis();
  }
}

void m1_encoder_isr() {
    bool a = digitalRead(M1_ENC_A);
    bool b = digitalRead(M1_ENC_B);
    m1_ticks += (a == b) ? -1 : 1;
}

void m2_encoder_isr() {
    bool a = digitalRead(M2_ENC_A);
    bool b = digitalRead(M2_ENC_B);
    m2_ticks += (a == b) ? 1 : -1;
}

void set_motor(int dir_pin, int pwm_pin, float speed) {
  speed = constrain(speed, -MAX_SPEED_MPS, MAX_SPEED_MPS);
  if (speed >= 0) {
    digitalWrite(dir_pin, HIGH);
    analogWrite(pwm_pin, (int)((speed / MAX_SPEED_MPS) * MAX_PWM));
  } else {
    digitalWrite(dir_pin, LOW);
    analogWrite(pwm_pin, (int)((-speed / MAX_SPEED_MPS) * MAX_PWM));
  }
}
