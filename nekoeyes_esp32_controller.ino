#include <WiFi.h>
#include <PubSubClient.h>

// WiFi credentials
const char* ssid = "Wokwi-GUEST";
const char* password = "";

// MQTT Configuration - NekoEyes
const char* mqtt_broker = "broker.mqttdashboard.com";
const int mqtt_port = 1883;
const char* mqtt_client_id = "nekoeyes_esp32_controller";

// Topics
const char* finger_distance_topic = "nekoeyes/finger_distance";
const char* led_topic = "nekoeyes/led";

// Pin definitions
const int LED_PIN = 2;           // Built-in LED
const int SERVO_PIN = 18;        // Servo control pin
const int STATUS_LED = 19;       // Status LED (green when connected)

WiFiClient wifiClient;
PubSubClient client(wifiClient);

// Variables
int current_distance = 0;
bool led_state = false;
bool mqtt_connected = false;

// Setup function
void setup() {
    Serial.begin(115200);
    delay(1000);
    
    Serial.println("🚀 NekoEyes ESP32 Controller Starting...");
    Serial.println("==========================================");
    
    // Initialize pins
    pinMode(LED_PIN, OUTPUT);
    pinMode(STATUS_LED, OUTPUT);
    pinMode(SERVO_PIN, OUTPUT);
    
    // Initial state
    digitalWrite(LED_PIN, LOW);
    digitalWrite(STATUS_LED, LOW);
    
    // Connect to WiFi
    connectToWiFi();
    
    // Setup MQTT
    client.setServer(mqtt_broker, mqtt_port);
    client.setCallback(onMqttMessage);
    
    // Connect to MQTT
    connectToMQTT();
}

void connectToWiFi() {
    Serial.print("🔄 Connecting to WiFi: ");
    Serial.println(ssid);
    
    WiFi.begin(ssid, password);
    
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    
    Serial.println();
    Serial.println("✅ WiFi connected!");
    Serial.print("📡 IP address: ");
    Serial.println(WiFi.localIP());
    
    // Turn on status LED when WiFi connected
    digitalWrite(STATUS_LED, HIGH);
}

void connectToMQTT() {
    while (!client.connected()) {
        Serial.print("🔄 Connecting to MQTT broker...");
        
        if (client.connect(mqtt_client_id)) {
            Serial.println(" ✅ Connected!");
            mqtt_connected = true;
            
            // Subscribe to NekoEyes topics
            client.subscribe(finger_distance_topic);
            client.subscribe(led_topic);
            
            Serial.println("📺 Subscribed to NekoEyes topics:");
            Serial.print("   • ");
            Serial.println(finger_distance_topic);
            Serial.print("   • ");
            Serial.println(led_topic);
            Serial.println("==========================================");
            
            // Blink status LED to indicate MQTT connection
            for (int i = 0; i < 6; i++) {
                digitalWrite(STATUS_LED, !digitalRead(STATUS_LED));
                delay(100);
            }
            digitalWrite(STATUS_LED, HIGH);
            
        } else {
            Serial.print(" ❌ Failed, rc=");
            Serial.print(client.state());
            Serial.println(" retrying in 5 seconds...");
            delay(5000);
        }
    }
}

void onMqttMessage(char* topic, byte* payload, unsigned int length) {
    // Convert payload to string
    String message = "";
    for (int i = 0; i < length; i++) {
        message += (char)payload[i];
    }
    
    String topicStr = String(topic);
    
    // Handle finger distance
    if (topicStr == finger_distance_topic) {
        current_distance = message.toInt();
        Serial.print("📏 Distance received: ");
        Serial.print(current_distance);
        Serial.println("px");
        
        // Map distance to servo angle (optional servo control)
        int servo_angle = map(constrain(current_distance, 0, 300), 0, 300, 0, 180);
        controlServo(servo_angle);
    }
    
    // Handle LED control
    else if (topicStr == led_topic) {
        if (message == "ON") {
            led_state = true;
            digitalWrite(LED_PIN, HIGH);
            Serial.println("💡 LED: ON 🟢");
        } else if (message == "OFF") {
            led_state = false;
            digitalWrite(LED_PIN, LOW);
            Serial.println("💡 LED: OFF 🔴");
        }
    }
}

void controlServo(int angle) {
    // Simple servo control using PWM
    // Map angle (0-180) to pulse width (1000-2000 microseconds)
    int pulseWidth = map(angle, 0, 180, 1000, 2000);
    
    // Generate PWM signal
    for (int i = 0; i < 10; i++) {
        digitalWrite(SERVO_PIN, HIGH);
        delayMicroseconds(pulseWidth);
        digitalWrite(SERVO_PIN, LOW);
        delayMicroseconds(20000 - pulseWidth);
    }
    
    Serial.print("🔄 Servo angle: ");
    Serial.println(angle);
}

void loop() {
    // Maintain MQTT connection
    if (!client.connected()) {
        mqtt_connected = false;
        digitalWrite(STATUS_LED, LOW);
        connectToMQTT();
    }
    
    client.loop();
    
    // Status indicator (heartbeat)
    static unsigned long lastHeartbeat = 0;
    if (millis() - lastHeartbeat > 2000) {
        lastHeartbeat = millis();
        
        Serial.print("💓 Heartbeat - Distance: ");
        Serial.print(current_distance);
        Serial.print("px, LED: ");
        Serial.print(led_state ? "ON" : "OFF");
        Serial.print(", WiFi: ");
        Serial.print(WiFi.status() == WL_CONNECTED ? "✅" : "❌");
        Serial.print(", MQTT: ");
        Serial.println(client.connected() ? "✅" : "❌");
    }
    
    delay(100);
}

void checkConnections() {
    // Check WiFi connection
    if (WiFi.status() != WL_CONNECTED) {
        Serial.println("❌ WiFi connection lost, reconnecting...");
        digitalWrite(STATUS_LED, LOW);
        connectToWiFi();
    }
    
    // Check MQTT connection
    if (!client.connected()) {
        Serial.println("❌ MQTT connection lost, reconnecting...");
        connectToMQTT();
    }
}
