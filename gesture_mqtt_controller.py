import cv2
import mediapipe as mp
import math
import numpy as np
import paho.mqtt.client as mqtt
import json
import time

# MQTT Configuration
MQTT_BROKER = "broker.hivemq.com"  # Free public broker, ganti dengan broker Anda
MQTT_PORT = 1883
MQTT_TOPIC = "esp32/servo/control"
MQTT_CLIENT_ID = "gesture_controller"

# solution APIs
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

# MQTT Client Setup
client = mqtt.Client(client_id=MQTT_CLIENT_ID)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
    else:
        print(f"Failed to connect, return code {rc}")

def on_publish(client, userdata, mid):
    print(f"Message published with mid: {mid}")

client.on_connect = on_connect
client.on_publish = on_publish

# Connect to MQTT broker
try:
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()
except Exception as e:
    print(f"Error connecting to MQTT broker: {e}")

# Webcam Setup
wCam, hCam = 640, 480
cam = cv2.VideoCapture(0)
cam.set(3, wCam)
cam.set(4, hCam)

# Variables for smoothing
last_servo_angle = 90
servo_angle = 90

# Mediapipe Hand Landmark Model
with mp_hands.Hands(
    model_complexity=0,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5) as hands:

    while cam.isOpened():
        success, image = cam.read()
        if not success:
            print("Ignoring empty camera frame.")
            continue

        # Flip image horizontally for a mirror effect
        image = cv2.flip(image, 1)
        
        # Convert BGR to RGB
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = hands.process(image)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        
        # Draw hand landmarks
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    image,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style()
                )

        # Extract hand landmarks
        lmList = []
        if results.multi_hand_landmarks:
            myHand = results.multi_hand_landmarks[0]
            for id, lm in enumerate(myHand.landmark):
                h, w, c = image.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append([id, cx, cy])

        # Process gesture for servo control
        if len(lmList) != 0:
            # Get thumb tip and index finger tip positions
            x1, y1 = lmList[4][1], lmList[4][2]  # Thumb tip
            x2, y2 = lmList[8][1], lmList[8][2]  # Index finger tip

            # Draw circles on fingertips
            cv2.circle(image, (x1, y1), 15, (255, 0, 0), cv2.FILLED)  # Blue for thumb
            cv2.circle(image, (x2, y2), 15, (0, 255, 0), cv2.FILLED)  # Green for index
            
            # Draw line between fingers
            cv2.line(image, (x1, y1), (x2, y2), (255, 255, 255), 3)
            
            # Calculate distance between thumb and index finger
            length = math.hypot(x2 - x1, y2 - y1)
            
            # Change line color when fingers are close
            if length < 50:
                cv2.line(image, (x1, y1), (x2, y2), (0, 0, 255), 3)  # Red when close

            # Map finger distance to servo angle (0-180 degrees)
            # Distance range: 20-250 pixels maps to 0-180 degrees
            servo_angle = np.interp(length, [20, 250], [0, 180])
            servo_angle = max(0, min(180, servo_angle))  # Clamp between 0-180
            
            # Smooth the servo movement
            servo_angle = int(last_servo_angle * 0.7 + servo_angle * 0.3)
            last_servo_angle = servo_angle

            # Send servo angle via MQTT
            try:
                message = {
                    "servo_angle": servo_angle,
                    "finger_distance": int(length),
                    "timestamp": time.time()
                }
                
                client.publish(MQTT_TOPIC, json.dumps(message))
                print(f"Sent: Servo Angle = {servo_angle}°, Distance = {int(length)}px")
                
            except Exception as e:
                print(f"Error publishing MQTT message: {e}")

            # Draw servo angle indicator
            cv2.rectangle(image, (50, 50), (250, 100), (0, 0, 0), 2)
            cv2.rectangle(image, (50, 50), (50 + int(servo_angle * 200 / 180), 100), (0, 255, 0), cv2.FILLED)
            cv2.putText(image, f'Servo: {servo_angle}°', (60, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Draw distance indicator
            cv2.putText(image, f'Distance: {int(length)}px', (60, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        # Draw instructions
        cv2.putText(image, 'Pinch fingers to control servo', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        cv2.putText(image, 'Press Q to quit', (10, image.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

        # Show the image
        cv2.imshow('Gesture Servo Controller', image)
        
        # Break loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# Cleanup
cam.release()
cv2.destroyAllWindows()
client.loop_stop()
client.disconnect()
print("Application closed.")
