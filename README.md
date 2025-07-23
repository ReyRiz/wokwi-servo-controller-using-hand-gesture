# 🐱 NekoEyes - Gesture-Controlled IoT System

A hand gesture recognition system that uses computer vision to control IoT devices via MQTT. When you move your thumb and index finger apart/together, it controls LED lights remotely!

## ✨ Features

- 👋 **Hand Gesture Detection** using MediaPipe
- 📏 **Finger Distance Measurement** between thumb and index finger
- 🔗 **MQTT Communication** for IoT device control
- 💡 **Smart LED Control** based on finger distance
- 🎯 **Real-time Processing** with live camera feed
- 🌐 **ESP32 Integration** for hardware control

## 🚀 How It Works

1. **Gesture Detection**: Camera captures hand gestures
2. **Distance Calculation**: Measures distance between thumb and index finger
3. **MQTT Publishing**: Sends distance data to MQTT broker
4. **LED Control**: ESP32 receives commands and controls LED
   - Distance > 100px → LED ON 🟢
   - Distance ≤ 100px → LED OFF 🔴

## 📋 Requirements

### Python Dependencies
```bash
pip install opencv-python
pip install mediapipe
pip install paho-mqtt
pip install numpy
```

### Hardware Components
- ESP32 Development Board
- LED (connected to pin 2)
- Status LED (connected to pin 19)
- Servo Motor (optional, connected to pin 18)
- Resistors (220Ω for LEDs)

## 🔧 Setup Instructions

### 1. Python Gesture Controller

```bash
# Clone or download the project
cd Gesture-Volume-Control

# Install dependencies
pip install -r requirements.txt

# Run the gesture controller
python nekoeyes_gesture_controller.py
```

### 2. ESP32 Setup

1. Open `nekoeyes_esp32_controller.ino` in Arduino IDE
2. Install required libraries:
   - WiFi
   - PubSubClient
3. Upload to ESP32
4. Open Serial Monitor to see connection status

### 3. Wokwi Simulation

1. Go to [wokwi.com](https://wokwi.com)
2. Create new ESP32 project
3. Copy the code from `nekoeyes_esp32_controller.ino`
4. Use the diagram from `nekoeyes_diagram.json`
5. Run simulation

## 📡 MQTT Configuration

**Broker**: `broker.mqttdashboard.com`  
**Port**: `1883`

**Topics**:
- `nekoeyes/finger_distance` - Publishes finger distance in pixels
- `nekoeyes/led` - Publishes LED commands (ON/OFF)

## 🎮 Usage

1. **Start the Python controller**:
   ```bash
   python nekoeyes_gesture_controller.py
   ```

2. **Show your hand** to the camera with thumb and index finger visible

3. **Control the LED**:
   - 🤏 Bring fingers close together → LED OFF
   - ✋ Spread fingers apart → LED ON

4. **Exit**: Press 'q' to quit

## 📊 Output Example

```
🎥 NekoEyes Gesture Controller Started!
✅ Connected to MQTT Broker (broker.mqttdashboard.com)!
📡 [1] Distance: 45px → LED: OFF
📡 [2] Distance: 120px → LED: ON
📡 [3] Distance: 80px → LED: OFF
```

## 🔗 Files Description

- `nekoeyes_gesture_controller.py` - Main Python gesture controller
- `nekoeyes_esp32_controller.ino` - ESP32 firmware code
- `nekoeyes_diagram.json` - Wokwi circuit diagram
- `nekoeyes_mqtt_test.py` - MQTT connection test script
- `wokwi.toml` - Wokwi project configuration

## 🛠️ Troubleshooting

### Python Issues
- **Camera not found**: Check if camera is connected and not used by other apps
- **MQTT connection failed**: Verify internet connection and broker address
- **Import errors**: Ensure all dependencies are installed

### ESP32 Issues
- **WiFi connection failed**: Check WiFi credentials in code
- **MQTT not connecting**: Verify broker address and port
- **LED not working**: Check wiring and pin connections

### Wokwi Issues
- **Simulation not loading**: Use browser version instead of VS Code extension
- **Library not found**: Try using built-in WiFi and PubSubClient libraries

## 🎯 Threshold Settings

Current LED control threshold: **100 pixels**

To change the threshold, modify this line in `nekoeyes_gesture_controller.py`:
```python
led_state = "ON" if distance > 100 else "OFF"  # Change 100 to your preferred value
```

## 🌟 Demo

The system can detect hand gestures in real-time and control IoT devices instantly. Perfect for:
- 🏠 Smart home automation
- 🎮 Gesture-based games
- 🤖 Robotics projects
- 📚 Educational IoT demonstrations

## 📈 Future Enhancements

- 🎯 Multiple gesture recognition
- 📱 Mobile app integration
- 🔊 Voice control combination
- 🎨 Custom LED patterns
- 📊 Data logging and analytics

---

**Made with ❤️ for IoT enthusiasts and gesture control lovers!**

*Happy coding! 🐱✨*
