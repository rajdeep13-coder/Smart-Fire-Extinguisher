# Technical Details

## System Overview

The Edge-ML based Smart Fire Extinguisher is designed as a locally controlled, vision-guided fire detection and suppression platform. Its architecture combines edge computer vision, environmental sensor fusion, geometric target alignment, and servo or pump actuation into one autonomous response loop.


## 1. Perception & Edge Inference

- A wide-angle camera captures continuous video frames at the monitored site.
- An on-device edge computing module runs a quantized **YOLOv8** object detection model to identify flame classes in real time.
- Flame centroid coordinates $(x_c, y_c)$ and bounding box dimensions are calculated directly on-chip with zero cloud reliance.

For a detected flame bounding box with upper-left coordinate $(x_1, y_1)$ and lower-right coordinate $(x_2, y_2)$, the image-space centroid is calculated as:

$$
x_c = \frac{x_1 + x_2}{2}, \qquad y_c = \frac{y_1 + y_2}{2}
$$

The edge module should publish the detection class, confidence score, centroid, bounding-box dimensions, and frame timestamp to the actuation controller. Keeping this inference local avoids dependence on a remote server and reduces response time during network outages.

## 2. Sensor Fusion & False-Positive Mitigation

Vision outputs are cross-referenced with auxiliary gas and smoke thresholds, such as those provided by MQ-series analog sensors.

Fire engagement is confirmed only when optical recognition matches environmental combustion markers. This confirmation rule reduces false alarms caused by red clothing, reflections, warm ambient lighting, or other objects that may resemble flames in a video frame.

A practical confirmation policy can require:

1. A flame-class detection above a configured confidence threshold.
2. Detection persistence across multiple consecutive frames.
3. An analog smoke or gas value above its calibrated threshold, or an active digital gas-sensor alarm.
4. A valid distance measurement before the actuation command is accepted.

The current Arduino prototype already reads both analog and digital gas-sensor signals. It also uses an HC-SR04 distance threshold as its proximity trigger. The camera confidence and multi-frame persistence checks belong to the planned edge-inference layer.

## 3. Targeting & Dynamic Actuation

The calculated visual offsets are converted into precise angular displacements, $\Delta\theta_{\text{pan}}$ and $\Delta\theta_{\text{tilt}}$, matching the camera field-of-view geometry.

For a camera with horizontal field of view $FOV_x$, vertical field of view $FOV_y$, and image dimensions $W \times H$, a first-order pixel-to-angle conversion is:

$$
\Delta\theta_{\text{pan}} = \left(\frac{x_c - W/2}{W}\right)FOV_x
$$

$$
\Delta\theta_{\text{tilt}} = \left(\frac{y_c - H/2}{H}\right)FOV_y
$$

The signs and coordinate orientation must be calibrated against the physical servo installation. Lens distortion, camera mounting offset, servo zero position, and nozzle offset should be measured during commissioning rather than assumed.

A dedicated microcontroller translates these values into PWM commands for high-torque servo motors driving a dual-axis gimbal. The controller should enforce travel limits, rate limits, and a defined safe position before accepting a new target.

Once alignment is achieved, a driver circuit opens an electromechanical valve or engages a 12 V high-pressure DC water pump to suppress the target immediately. The high-current pump and valve path must be electrically isolated from the logic controller with an appropriately rated driver, flyback protection, fuse, and separate power supply.

Real-time operational states, distance metrics, and environmental gas indices are rendered via an integrated status display. In the current prototype, the SSD1306 OLED reports distance, smoke value, threshold, scan angle, lock angle, and system state.

## 4. Key Features & Technical Specifications

### On-Device Edge Computing

All neural network operations execute locally, guaranteeing zero network latency and operation during network or power disruptions. The selected edge module must have enough compute, memory, and thermal capacity for the quantized YOLOv8 model and the intended camera frame rate.

### Pinpoint Active Targeting

The system directs suppression fluid at the flame origin, minimizing surrounding resource damage and conserving water. Accurate targeting depends on camera calibration, stable mechanical mounting, distance estimation, nozzle alignment, and a controlled spray pattern.

### Continuous Multi-Angle Sweep & Lock

The system can transition between an autonomous scanning routine and an active-tracking locked state. The current firmware demonstrates this behavior with the following states:

| State | Prototype behavior |
| --- | --- |
| `NORMAL` | Monitors sensors and parks both servos at 90°. |
| `SCANNING` | Sweeps from 30° to 150° in 5° increments and records the shortest ultrasonic reading. |
| `LOCKED` | Holds the best angle and re-scans every 3 seconds while the threat remains active. |

### Modular Multi-Sensor Fusion

The architecture combines optical detection with chemical smoke sensing for high-reliability triggering. Additional modules can be added behind the sensor-fusion interface, including thermal sensing, ambient-light compensation, redundant distance sensing, or an emergency manual stop.

## 5. Potential Applications

- **Industrial Facilities & Warehouses:** Rapid suppression in high-density rack storage before main ceiling systems deploy.
- **Server Rooms & Battery Storage:** Immediate localized intervention for lithium-ion battery or rack-level electrical ignitions.
- **Commercial Kitchens & Laboratories:** Targeted containment in volatile chemical or cooking environments where instant response is crucial.

These applications require domain-specific fire suppression media, enclosure ratings, certification, maintenance procedures, and human override controls. The prototype should not be deployed in an occupied or hazardous environment without formal safety validation.

## Prototype-to-Production Mapping

| Full-system capability | Current repository implementation |
| --- | --- |
| Wide-angle camera | Not included in `diagram.json` |
| Quantized YOLOv8 inference | Not included in `sketch.ino` |
| Flame centroid and bounding box | Planned edge-module output |
| MQ-series analog/digital sensing | Implemented on A1 and D2 |
| Distance measurement | Implemented with HC-SR04 on D8/D7 |
| Servo targeting | Implemented as synchronized single-axis sweep on D11/D10 |
| OLED operational display | Implemented with SSD1306 at I2C address `0x3C` |
| Valve or 12 V pump control | Not included; requires a separate protected driver stage |
