# Gesture Servo Controller dengan ESP32 dan MQTT

Project ini mengintegrasikan gesture control tangan dengan ESP32 menggunakan MQTT untuk mengontrol servo motor.

## Komponen yang Dibutuhkan

### Software:
- Python 3.11+ dengan library:
  - OpenCV
  - MediaPipe
  - NumPy
  - paho-mqtt
- Arduino IDE atau Platform.io
- Wokwi Simulator (untuk simulasi ESP32)

### Hardware (untuk implementasi fisik):
- ESP32 Development Board
- Servo Motor (SG90 atau serupa)
- Kabel jumper
- Breadboard (opsional)

## Struktur Project

```
├── gesture_mqtt_controller.py    # Kode Python untuk gesture control
├── esp32_servo_controller.ino    # Kode Arduino untuk ESP32
├── wokwi_diagram.json           # Konfigurasi simulasi Wokwi
├── main.py                      # Kode original volume control
└── main copy.py                 # Backup kode original
```

## Cara Penggunaan

### 1. Simulasi di Wokwi

1. Buka [Wokwi.com](https://wokwi.com)
2. Buat project baru ESP32
3. Copy kode dari `esp32_servo_controller.ino` ke editor
4. Copy konfigurasi dari `wokwi_diagram.json` ke diagram.json
5. Tambahkan library berikut di libraries.txt:
   ```
   PubSubClient
   ESP32Servo
   ArduinoJson
   ```
6. Jalankan simulasi

### 2. Menjalankan Gesture Controller

```bash
# Install dependencies
pip install opencv-python mediapipe numpy paho-mqtt

# Jalankan gesture controller
python gesture_mqtt_controller.py
```

### 3. Konfigurasi MQTT

#### Untuk Testing (menggunakan public broker):
- Broker: `broker.hivemq.com`
- Port: `1883`
- Topic: `esp32/servo/control`

#### Untuk Production (menggunakan broker pribadi):
Ganti konfigurasi MQTT di kedua file:

**Python (gesture_mqtt_controller.py):**
```python
MQTT_BROKER = "your-broker-address"
MQTT_PORT = 1883
MQTT_TOPIC = "esp32/servo/control"
```

**Arduino (esp32_servo_controller.ino):**
```cpp
const char* mqtt_server = "your-broker-address";
const int mqtt_port = 1883;
const char* mqtt_topic = "esp32/servo/control";
```

## Cara Kerja

1. **Gesture Detection**: Camera mendeteksi tangan dan mengukur jarak antara ibu jari dan telunjuk
2. **MQTT Communication**: Data jarak dikirim via MQTT ke ESP32
3. **Servo Control**: ESP32 menerima data dan menggerakkan servo sesuai gesture

## Kalibrasi Gesture

- **Jarak minimum** (20px): Servo posisi 0°
- **Jarak maksimum** (250px): Servo posisi 180°
- **Smoothing**: Gerakan servo dihaluskan untuk mengurangi jitter

## Troubleshooting

### Python Issues:
```bash
# Jika ada error NumPy
pip install "numpy>=1.26.0,<2.2.0"

# Jika ada error OpenCV
pip install opencv-python==4.8.1.78
```

### ESP32 Issues:
- Pastikan WiFi credentials benar
- Periksa koneksi pin servo (VCC=VIN, GND=GND, Signal=D18)
- Monitor serial untuk debug messages

### MQTT Issues:
- Gunakan MQTT client seperti MQTT Explorer untuk testing
- Periksa firewall settings
- Pastikan broker accessible

## Pinout ESP32

```
ESP32 Pin  |  Servo Pin
-----------|------------
VIN        |  VCC (Red)
GND        |  GND (Black)
D18        |  Signal (Orange/Yellow)
```

## Pengembangan Lanjutan

1. **Multiple Servos**: Tambah servo untuk control sumbu X dan Y
2. **Gesture Recognition**: Tambah gesture lain (fist, peace sign, etc.)
3. **Local Network**: Setup MQTT broker lokal dengan Mosquitto
4. **Mobile App**: Buat mobile app untuk monitoring
5. **Computer Vision**: Tambah object detection dan tracking

## Kontribusi

Silakan buat pull request atau issue untuk perbaikan dan pengembangan.

## Lisensi

MIT License - bebas digunakan untuk keperluan pembelajaran dan komersial.
