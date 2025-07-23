import cv2
import mediapipe as mp
import math
import numpy as np
import paho.mqtt.client as mqtt
import json
import time

# MQTT Configuration - ReyRiz
MQTT_BROKER = "broker.mqttdashboard.com"  # Broker yang diminta
MQTT_PORT = 1883
FINGER_DISTANCE_TOPIC = "reyriz/finger_distance"  # Topic untuk finger distance
LED_TOPIC = "reyriz/led"                          # Topic untuk LED control
MQTT_CLIENT_ID = "reyriz_gesture_controller"

# solution APIs
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

# MQTT Client Setup
client = mqtt.Client(client_id=MQTT_CLIENT_ID)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Connected to MQTT Broker (broker.mqttdashboard.com)!")
        print(f"📡 Publishing to:")
        print(f"   • {FINGER_DISTANCE_TOPIC} (finger distance values)")
        print(f"   • {LED_TOPIC} (LED ON/OFF commands)")
        print("=" * 60)
    else:
        print(f"❌ Failed to connect, return code {rc}")

def on_publish(client, userdata, mid):
    print(f"📤 Message published (mid: {mid})")

client.on_connect = on_connect
client.on_publish = on_publish

# Connect to MQTT broker
try:
    print("🔄 Connecting to broker.mqttdashboard.com...")
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()
    time.sleep(2)  # Wait for connection
except Exception as e:
    print(f"❌ Error connecting to MQTT broker: {e}")

# Webcam Setup - Responsive resolution
wCam, hCam = 1280, 720  # Higher initial resolution for better quality
cam = cv2.VideoCapture(0)
cam.set(3, wCam)
cam.set(4, hCam)

# Window setup for responsive display
cv2.namedWindow('NekoEyes Gesture Controller', cv2.WINDOW_NORMAL)
cv2.resizeWindow('NekoEyes Gesture Controller', 800, 600)

# Variables for tracking
last_finger_distance = 0
last_led_state = "off"
message_count = 0
last_publish_time = 0
publish_interval = 1.0  # Publish every 1 second to avoid overload

print("🎥 NekoEyes Gesture Controller Started!")
print("🎮 Controls:")
print("   ✋ Show hand with thumb and index finger")
print("   📏 Finger distance > 100px → LED ON")
print("   📏 Finger distance < 100px → LED OFF")
print("   ❌ Press 'q' to quit")
print("=" * 60)

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

        # Process gesture for finger distance and LED control
        if len(lmList) != 0:
            # Get thumb tip and index finger tip positions
            x1, y1 = lmList[4][1], lmList[4][2]  # Thumb tip
            x2, y2 = lmList[8][1], lmList[8][2]  # Index finger tip

            # Draw circles on fingertips
            cv2.circle(image, (x1, y1), 15, (255, 0, 0), cv2.FILLED)  # Blue for thumb
            cv2.circle(image, (x2, y2), 15, (0, 255, 0), cv2.FILLED)  # Green for index
            
            # Draw line between fingers
            cv2.line(image, (x1, y1), (x2, y2), (255, 255, 0), 3)  # Yellow line
            
            # Calculate distance between thumb and index finger
            finger_distance = int(math.hypot(x2 - x1, y2 - y1))
            
            # Determine LED state based on finger distance
            led_state = "on" if finger_distance > 100 else "off"
            
            # Change line color based on LED state
            if led_state == "on":
                cv2.line(image, (x1, y1), (x2, y2), (0, 255, 0), 5)  # Green when LED ON
            else:
                cv2.line(image, (x1, y1), (x2, y2), (0, 0, 255), 5)  # Red when LED OFF

            # Publish to MQTT with rate limiting (1 second interval)
            current_time = time.time()
            if (current_time - last_publish_time > publish_interval or 
                led_state != last_led_state):  # Only publish on LED state change or 1 second interval
                
                try:
                    # Publish finger distance to nekoeyes/finger_distance
                    client.publish(FINGER_DISTANCE_TOPIC, str(finger_distance))
                    
                    # Publish LED state to nekoeyes/led
                    client.publish(LED_TOPIC, led_state)
                    
                    message_count += 1
                    print(f"📡 [{message_count}] Distance: {finger_distance}px → LED: {led_state}")
                    
                    last_finger_distance = finger_distance
                    last_led_state = led_state
                    last_publish_time = current_time
                    
                except Exception as e:
                    print(f"❌ Error publishing MQTT message: {e}")

            # Visual feedback on image
            # LED status indicator
            # led_color = (0, 255, 0) if led_state == "on" else (0, 0, 255)
            # cv2.rectangle(image, (50, 50), (300, 90), led_color, -1)
            # cv2.putText(image, f'LED: {led_state}', (60, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            
            # Distance indicator
            # cv2.rectangle(image, (50, 100), (300, 140), (0, 0, 0), 2)
            # distance_bar_width = min(int(finger_distance * 250 / 300), 250)
            # bar_color = (0, 255, 0) if finger_distance > 100 else (0, 0, 255)
            # cv2.rectangle(image, (50, 100), (50 + distance_bar_width, 140), bar_color, -1)
            # cv2.putText(image, f'Distance: {finger_distance}px', (60, 125), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            # Threshold line indicator
            # threshold_x = 50 + int(100 * 250 / 300)  # Position for 100px threshold
            # cv2.line(image, (threshold_x, 95), (threshold_x, 145), (255, 255, 255), 2)
            # cv2.putText(image, '100', (threshold_x - 15, 155), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # Message counter
            # cv2.putText(image, f'Messages: {message_count}', (50, 170), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

        else:
            # No hand detected
            cv2.putText(image, '🖐️ Show your hand', (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        # Draw title and instructions
        # cv2.putText(image, 'NekoEyes Gesture Controller', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        # cv2.putText(image, 'Distance > 100px = LED ON', (10, image.shape[0] - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        # cv2.putText(image, 'Distance < 100px = LED OFF', (10, image.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        cv2.putText(image, 'Press Q to quit', (10, image.shape[0] - 2), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

        # Show the image with responsive window
        cv2.imshow('NekoEyes Gesture Controller', image)
        
        # Auto-resize window to maintain aspect ratio
        window_size = cv2.getWindowImageRect('NekoEyes Gesture Controller')
        if window_size[2] > 0 and window_size[3] > 0:  # Check if window dimensions are valid
            aspect_ratio = image.shape[1] / image.shape[0]
            new_height = int(window_size[2] / aspect_ratio)
            if abs(new_height - window_size[3]) > 10:  # Only resize if significant difference
                cv2.resizeWindow('NekoEyes Gesture Controller', window_size[2], new_height)
        
        # Break loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# Cleanup
cam.release()
cv2.destroyAllWindows()
client.loop_stop()
client.disconnect()
print("\n🔚 NekoEyes Gesture Controller stopped")
print(f"📊 Total messages sent: {message_count}")
print("👋 Goodbye!")
