# EDGE-ML Based Smart Fire Extinguisher System

![IoT](https://img.shields.io/badge/IoT-Project-blue?style=for-the-badge)
![Hackathon](https://img.shields.io/badge/IoTricity-S3-blue?style=for-the-badge)
![ML](https://img.shields.io/badge/Machine-Learning-purple?style=for-the-badge)
![Arduino](https://img.shields.io/badge/Arduino-C++-lightblue?style=for-the-badge)
[![Open in Wokwi](https://img.shields.io/badge/Simulate%20in-Wokwi-00a98f?logo=wokwi&logoColor=white)](https://wokwi.com/)

The Edge ML–Based Autonomous Fire Extinguisher is a real-time, vision-guided safety system designed to detect, track, and extinguish localized fires autonomously without human intervention. By replacing conventional proximity-based scanning methods with an optimized YOLOv8 computer vision model running entirely on local edge hardware, the system accurately extracts spatial coordinates of active flames from camera feeds. These visual coordinates are coupled with environmental verification sensors to dynamically direct a two-axis servo-actuated water cannon and deploy a suppression payload with sub-second response times.

For technical details and future scope, see [details.md](details.md).

<p align="center">
  <a href="https://github.com/rajdeep13-coder/Smart-Fire-Extinguisher">
    <img src="/assets/circuit_sketch.jpeg" />
  </a>
</p>

# Wokwi Simulation: <a href="https://wokwi.com/projects/476314925594840065">

## The Problem
Traditional automated fire suppression systems—such as ceiling-mounted thermal glass-bulb sprinklers—suffer from notable limitations:
-Delayed Response: They require ambient ceiling temperatures to exceed critical thresholds before activating, allowing flames to spread significantly.
-Collateral Water Damage: Sprinklers flood broad zones rather than targeting the localized base of the flame.
-Limited Spatial Intelligence: Ultrasonic- and basic IR-based prototypes sweep mechanically across broad zones with high false-positive rates and struggle to distinguish actual flame contours from warm bodies or physical obstacles.

## Features

- Monitors an analog gas/smoke sensor and its digital alarm output.
- Measures target distance with an HC-SR04 ultrasonic sensor.
- Uses a potentiometer to adjust the smoke threshold while running.
- Sweeps both servos from 30° through 150° in 5° increments.
- Locks both cannon servos to the angle with the shortest measured distance.
- Re-scans every 3 seconds while a threat remains active.
- Displays distance, smoke level, threshold, and system state on a 128x64 I2C OLED.
- Activates a 2 kHz buzzer and red LED during scanning or lock-on.
- Shows a green LED when the system is in the normal state.
- Sends state and sensor telemetry to the serial monitor at 115200 baud.

## How It Works

The controller runs three states:

| State | Behavior |
| --- | --- |
| `NORMAL` | Reads sensors, parks both servos at 90°, turns the alarm off, and waits for a threat. |
| `SCANNING` | Sweeps from 30° to 150°, samples distance at each step, and remembers the shortest reading. |
| `LOCKED` | Holds both servos at the best angle, keeps the alarm active, and periodically re-scans. |

A threat starts when either condition is true:

- Ultrasonic distance is below **50 cm**. (for demo pupose)
- Analog smoke value is above the potentiometer-controlled threshold, or the gas sensor digital output is active.

The smoke threshold is mapped from a potentiometer reading of `0-1023` to a usable range of `100-800`.

## Hardware

### Components

- Arduino Uno
- 2 servo motors for the water-cannon direction
- HC-SR04 ultrasonic distance sensor
- MQ-style gas/smoke sensor with analog and digital outputs
- 128x64 SSD1306 I2C OLED display
- 5 V buzzer
- Red and green LEDs
- 2 x 1 kΩ resistors for the LEDs
- 10 kΩ potentiometer for smoke-threshold adjustment
- Breadboard and jumper wires

### Pinout

| Component | Signal | Arduino pin | Purpose |
| --- | --- | ---: | --- |
| Left servo | PWM | D11 | Cannon 1 angle |
| Right servo | PWM | D10 | Cannon 2 angle |
| HC-SR04 | TRIG | D8 | Ultrasonic trigger |
| HC-SR04 | ECHO | D7 | Ultrasonic return pulse |
| Gas sensor | AOUT | A1 | Analog smoke reading |
| Gas sensor | DOUT | D2 | Digital smoke alarm |
| Buzzer | Signal | D12 | 2 kHz alarm tone |
| Red LED | Anode through resistor | D6 | Threat indicator |
| Green LED | Anode through resistor | D3 | Normal-state indicator |
| Potentiometer | Wiper | A0 | Smoke-threshold control |
| SSD1306 OLED | SDA | A4 | I2C data |
| SSD1306 OLED | SCL | A5 | I2C clock |


## OLED and Serial Output

The OLED uses I2C address `0x3C` and displays:

- Current ultrasonic distance
- Current analog smoke value and threshold
- `NORMAL`, `SCANNING`, or `LOCKED` state
- Scan angle and best distance while scanning
- Locked angle and range after target acquisition

Example serial messages:

```text
== IOTRICITY S3 — Smart Fire Extinguisher ==
System ready.
>> Threat detected — starting scan
>> LOCKED at 85° — dist 24.7 cm
State=LOCKED | Dist=24.7cm | Smoke=416/300 | Aim=85°
```

<p align="center">
  <a href="https://github.com/rajdeep13-coder/Smart-Fire-Extinguisher">
    <img src="/assets/wokwi simulation.jpeg" />
  </a>
</p>

## Configuration

The main thresholds and timing values are defined near the top of `sketch.ino`:

| Constant | Default | Description |
| --- | ---: | --- |
| `DISTANCE_THRESHOLD_CM` | `50` | Distance below which a fire is considered nearby |
| `DEFAULT_SMOKE_THRESH` | `300` | Initial analog smoke threshold |
| `SERVO_SCAN_MIN` | `30°` | Minimum scan angle |
| `SERVO_SCAN_MAX` | `150°` | Maximum scan angle |
| `SERVO_SCAN_STEP` | `5°` | Angle increment per scan sample |
| `SCAN_STEP_DELAY_MS` | `60` | Servo settling time between samples |
| `RESCAN_INTERVAL_MS` | `3000` | Delay before re-scanning while locked |
| `ALARM_TONE_HZ` | `2000` | Buzzer frequency |

```


📢 Developed for IoTricity-S3 Hackathon by Assymetricals