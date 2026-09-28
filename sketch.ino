#include <Servo.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);

#define SERVO1_PIN 11
#define SERVO2_PIN 10
#define TRIG_PIN 8
#define ECHO_PIN 7
#define GAS_ANALOG_PIN A1
#define GAS_DIGITAL_PIN 2
#define BUZZER_PIN 12
#define RED_LED_PIN 6
#define GREEN_LED_PIN 3
#define RELAY_PIN 4
#define POT_PIN A0

Servo servo1;
Servo servo2;

unsigned long lastSignalTime = 0;
bool fireActive = false;

int currentAngle = 90;
float distanceCm = 0;
int smokeVal = 0;
int smokeThresh = 300;
unsigned long lastOledUpdate = 0;

void setup() {
  Serial.begin(115200);
  
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  pinMode(GAS_DIGITAL_PIN, INPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(RED_LED_PIN, OUTPUT);
  pinMode(GREEN_LED_PIN, OUTPUT);
  pinMode(RELAY_PIN, OUTPUT);
  
  digitalWrite(RELAY_PIN, LOW);
  digitalWrite(GREEN_LED_PIN, HIGH);
  digitalWrite(RED_LED_PIN, LOW);

  servo1.attach(SERVO1_PIN);
  servo2.attach(SERVO2_PIN);
  servo1.write(90);
  servo2.write(90);

  if(!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println(F("OLED init failed"));
  } else {
    display.clearDisplay();
    display.setTextColor(SSD1306_WHITE);
    display.setTextSize(1);
    display.setCursor(10, 20);
    display.println("Smart Extinguisher");
    display.setCursor(10, 40);
    display.println("Waiting for PC...");
    display.display();
  }
}

float getDistance() {
  digitalWrite(TRIG_PIN, LOW); delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH); delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);
  long duration = pulseIn(ECHO_PIN, HIGH, 30000);
  if (duration == 0) return 999.0;
  return (duration * 0.0343) / 2.0;
}

void updateOLED() {
  if (millis() - lastOledUpdate < 250) return;
  lastOledUpdate = millis();

  display.clearDisplay();
  display.setTextSize(1);
  display.setCursor(0, 0);
  display.print("Fire: ");
  display.println(fireActive ? "DETECTED!" : "None");
  
  display.setCursor(0, 16);
  display.print("Dist: ");
  display.print(distanceCm, 1);
  display.println(" cm");
  
  display.setCursor(0, 32);
  display.print("Smoke: ");
  display.print(smokeVal);
  display.print(" / ");
  display.println(smokeThresh);

  display.setCursor(0, 48);
  display.print("Angle: ");
  display.print(currentAngle);
  display.display();
}

void loop() {
  // 1. Read PC commands (Coordinate from YOLO)
  while (Serial.available() > 0) {
    String data = Serial.readStringUntil('\n');
    data.trim();
    if (data.startsWith("X:")) {
      int commaIdx = data.indexOf(',');
      if (commaIdx > 0) {
        int x = data.substring(2, commaIdx).toInt();
        // Assuming video width is 640. Map X to Servo angle 150 to 30 degrees.
        currentAngle = map(x, 0, 640, 150, 30);
        currentAngle = constrain(currentAngle, 30, 150);
        
        lastSignalTime = millis();
        fireActive = true;
      }
    }
  }

  // 2. Read Sensors (Distance & Smoke) continuously
  distanceCm = getDistance();
  smokeVal = analogRead(GAS_ANALOG_PIN);
  smokeThresh = map(analogRead(POT_PIN), 0, 1023, 100, 800);

  // 3. Process Actions
  if (fireActive) {
    // If no coordinates received for 2 seconds, assume fire is gone
    if (millis() - lastSignalTime > 2000) {
      fireActive = false;
    }
  }

  if (fireActive) {
    // Turn Servos to target Coordinate
    servo1.write(currentAngle);
    servo2.write(currentAngle);
    
    // Turn on Relay (Pump) & Indicators
    digitalWrite(RELAY_PIN, HIGH);
    digitalWrite(RED_LED_PIN, HIGH);
    digitalWrite(GREEN_LED_PIN, LOW);
    tone(BUZZER_PIN, 2000);
  } else {
    // Park Servos to center
    currentAngle = 90;
    servo1.write(currentAngle);
    servo2.write(currentAngle);
    
    // Turn off Relay (Pump) & Indicators
    digitalWrite(RELAY_PIN, LOW);
    digitalWrite(RED_LED_PIN, LOW);
    digitalWrite(GREEN_LED_PIN, HIGH);
    noTone(BUZZER_PIN);
  }

  // 4. Update OLED Display
  updateOLED();
}
