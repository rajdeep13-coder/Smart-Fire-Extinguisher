import cv2
import time
import threading
import socket
import serial
from ultralytics import YOLO

# Configuration
MAIN_MODEL_PATH = "fire_model.pt"  # A heavier model could be placed here later
LIGHT_MODEL_PATH = "fire_model.pt" # Local light model
WIFI_CHECK_INTERVAL = 2.0       # Check every 2 seconds
WIFI_TIMEOUT = 5.0              # 5 seconds time limit to switch
PING_HOST = "8.8.8.8"           # Google DNS to check internet
PING_PORT = 53

# Global state
is_wifi_connected = True
current_model = None
lock = threading.Lock()

# Arduino Serial Configuration
# UPDATE 'COM3' to the correct port for your Arduino (e.g., 'COM5', '/dev/ttyUSB0', etc.)
try:
    arduino = serial.Serial('COM3', 9600, timeout=1)
    time.sleep(2) # Allow Arduino to reboot after connection
    print("Arduino connected on COM3")
except Exception as e:
    arduino = None
    print(f"Arduino connection failed: {e}. Running without hardware control.")

def check_connection(host=PING_HOST, port=PING_PORT, timeout=3):
    """Check if there is an active internet connection."""
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error:
        return False

def network_monitor():
    """Background thread to monitor network connectivity and switch models."""
    global is_wifi_connected, current_model
    
    # Initialize models (in a real app, you might lazy-load them to save memory)
    print("Loading models...")
    main_model = YOLO(MAIN_MODEL_PATH)
    light_model = YOLO(LIGHT_MODEL_PATH)
    print("Models loaded.")

    with lock:
        current_model = main_model

    last_connected_time = time.time()

    while True:
        connected = check_connection()
        
        with lock:
            if connected:
                if not is_wifi_connected:
                    print("[Network] Wi-Fi restored! Switching back to MAIN model.")
                is_wifi_connected = True
                current_model = main_model
                last_connected_time = time.time()
            else:
                # If disconnected for more than the timeout (5 seconds limit)
                if is_wifi_connected and (time.time() - last_connected_time) >= WIFI_TIMEOUT:
                    print("[Network] Wi-Fi lost for 5 seconds! Switching to LOCAL LIGHT model.")
                    is_wifi_connected = False
                    current_model = light_model
        
        time.sleep(WIFI_CHECK_INTERVAL)

def classify_fire_type(box, frame):
    """
    Placeholder function to classify the type of fire.
    In a real project, this would either be part of the YOLO model's classes 
    (e.g., class 0: short-circuit fire, class 1: spark fire) 
    or a secondary classification model that crops the fire box and classifies it.
    """
    # Dummy logic for demonstration
    # You would replace this with actual model inference or logic based on the detected box
    fire_types = ["Generic Fire", "Short-Circuit Fire", "Spark Fire"]
    return fire_types[0] # Defaulting to generic for this demo

def main():
    global current_model

    # Start network monitor thread
    monitor_thread = threading.Thread(target=network_monitor, daemon=True)
    monitor_thread.start()

    # Wait for the model to be initially loaded
    while current_model is None:
        time.sleep(0.1)

    # Open webcam or video file (0 for default webcam)
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open video source.")
        return

    print("Starting video stream...")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Get the current model safely
        with lock:
            active_model = current_model
            network_status = "Main Model (Online)" if is_wifi_connected else "Light Model (Offline)"

        # Run inference
        results = active_model(frame, stream=True, verbose=False)

        for result in results:
            boxes = result.boxes
            for box in boxes:
                # In standard YOLOv8, class 0 is person, etc. 
                # You MUST train a custom YOLO model on a fire dataset.
                # Assuming class '0' is fire in your custom trained model for this example.
                cls = int(box.cls[0])
                conf = float(box.conf[0])
                
                if conf > 0.05: 
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    
                    # Get the actual class name from the model
                    class_name = active_model.names[cls]
                    
                    # Only display bounding box and label if "fire" is detected
                    if class_name.lower() == "fire":
                        label = f"Fire {conf:.2f}"
                        
                        # Calculate center coordinates for Arduino targeting
                        cx = (x1 + x2) // 2
                        cy = (y1 + y2) // 2

                        # Print coordinates to your computer's terminal
                        print(f"Fire Target -> X:{cx}, Y:{cy}")

                        # Send coordinates to Arduino if connected
                        if arduino is not None:
                            # Format: "X:123,Y:456\n"
                            command = f"X:{cx},Y:{cy}\n"
                            arduino.write(command.encode('utf-8'))

                        # Draw bounding box, label, and center targeting point
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                        cv2.circle(frame, (cx, cy), 5, (0, 255, 0), -1)
                        cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

        # Display network status on screen
        color = (0, 255, 0) if is_wifi_connected else (0, 0, 255)
        cv2.putText(frame, f"Status: {network_status}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

        cv2.imshow('Fire Detection System', frame)

        # Press 'q' to quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
