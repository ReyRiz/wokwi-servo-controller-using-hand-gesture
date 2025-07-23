# Wokwi ESP32 Servo Controller Setup

## Link Wokwi Project Template
[Buka Template di Wokwi](https://wokwi.com/projects/new/esp32)

## Langkah-langkah Setup di Wokwi:

### 1. Buat Project Baru ESP32
- Pilih "ESP32" di Wokwi
- Delete kode default di sketch.ino

### 2. Copy Kode Arduino
Copy seluruh kode dari file `esp32_servo_controller.ino` ke editor Wokwi

### 3. Setup Libraries
Klik tab "Libraries" dan tambahkan:
```
PubSubClient
ESP32Servo
ArduinoJson
```

### 4. Setup Diagram
Klik "Add Part" dan tambahkan:
- **Servo Motor**: Wokwi Servo
- Hubungkan koneksi:
  - ESP32 VIN → Servo V+ (kabel merah)
  - ESP32 GND → Servo GND (kabel hitam) 
  - ESP32 D18 → Servo PWM (kabel kuning/orange)

### 5. Konfigurasi diagram.json (Opsional)
Jika ingin menggunakan konfigurasi otomatis, copy kode dari `wokwi_diagram.json`

### 6. Test Simulasi
- Klik tombol "Start Simulation"
- Buka Serial Monitor untuk melihat log
- Pastikan ESP32 terhubung ke WiFi dan MQTT broker

## Testing MQTT Connection

### Menggunakan MQTT Explorer (Recommended):
1. Download [MQTT Explorer](http://mqtt-explorer.com/)
2. Connect ke broker: `broker.hivemq.com:1883`
3. Subscribe ke topic: `esp32/servo/control`
4. Publish manual message untuk test:
```json
{
  "servo_angle": 90,
  "finger_distance": 100,
  "timestamp": 1642678800
}
```

### Menggunakan Python Script:
Jalankan `gesture_mqtt_controller.py` dan gerakkan tangan di depan camera

## Expected Behavior:

1. **ESP32 Startup**: 
   - Serial menampilkan "Starting ESP32 Servo Controller..."
   - Koneksi WiFi berhasil
   - MQTT connection berhasil
   - Subscribe ke topic berhasil

2. **Servo Movement**:
   - Servo bergerak sesuai dengan data yang diterima
   - Serial menampilkan: "Servo moved to: XXX° (finger distance: XXXpx)"

3. **Auto Return**:
   - Jika tidak ada pesan selama 5 detik, servo kembali ke posisi 90°

## Troubleshooting:

### ESP32 tidak terhubung WiFi:
- Pastikan menggunakan "Wokwi-GUEST" sebagai SSID
- Password kosong untuk Wokwi WiFi

### MQTT Connection Failed:
- Cek internet connection di Wokwi
- Ganti broker jika `broker.hivemq.com` tidak accessible
- Alternative brokers:
  - `test.mosquitto.org`
  - `mqtt.eclipse.org`

### Servo tidak bergerak:
- Periksa wiring diagram
- Pastikan pin 18 digunakan untuk servo PWM
- Cek serial monitor untuk error messages

### JSON Parsing Error:
- Pastikan format JSON benar
- Check message format dari Python script

## Advanced Configuration:

### Custom MQTT Broker:
Ganti di kode ESP32:
```cpp
const char* mqtt_server = "your-broker.com";
const int mqtt_port = 1883;
```

### Multiple Servos:
Tambah servo kedua dengan menambah:
```cpp
const int servoPin2 = 19;
Servo myServo2;
```

### Different Servo Range:
Modifikasi mapping angle:
```cpp
servoAngle = map(servoAngle, 0, 180, 30, 150); // Custom range
```

## Monitoring Commands:

Serial Monitor akan menampilkan:
```
Starting ESP32 Servo Controller...
Connecting to Wokwi-GUEST
.....
WiFi connected
IP address: 192.168.1.XXX
Attempting MQTT connection...connected
Subscribed to topic: esp32/servo/control
Message received on topic: esp32/servo/control
Message: {"servo_angle":120,"finger_distance":80,"timestamp":1642678800}
Servo moved to: 120° (finger distance: 80px)
```
