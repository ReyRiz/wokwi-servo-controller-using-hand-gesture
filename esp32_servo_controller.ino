#include <WiFi.h>
#include <PubSubClient.h>
#include <ESP32Servo.h>
#include <ArduinoJson.h>

// WiFi credentials (gunakan WiFi simulator di Wokwi)
const char* ssid = "Wokwi-GUEST";
const char* password = "";

// MQTT Broker settings
const char* mqtt_server = "broker.hivemq.com";
const int mqtt_port = 1883;
const char* servo_topic = "esp32/servo/angle";        // Topic untuk servo angle (value langsung)
const char* distance_topic = "esp32/servo/distance";  // Topic untuk finger distance  
const char* status_topic = "esp32/servo/status";      // Topic untuk status feedback
const char* client_id = "ESP32_Servo_Controller";

// Servo settings
const int servoPin = 18;  // Pin untuk servo
Servo myServo;

// WiFi and MQTT clients
WiFiClient espClient;
PubSubClient client(espClient);

// Variables
int currentServoAngle = 90;
unsigned long lastMessage = 0;

void setup() {
  Serial.begin(115200);
  Serial.println("Starting ESP32 Servo Controller...");
  
  // Initialize servo
  myServo.attach(servoPin);
  myServo.write(90);  // Start at middle position
  
  // Connect to WiFi
  setup_wifi();
  
  // Setup MQTT
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);
  
  Serial.println("Setup complete. Ready to receive servo commands via MQTT.");
}

void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void callback(char* topic, byte* payload, unsigned int length) {
  // Convert payload to string/number
  String message = "";
  for (int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  
  Serial.print("Message received on topic: ");
  Serial.println(topic);
  Serial.print("Value: ");
  Serial.println(message);
  
  // Handle different topics without JSON parsing
  if (strcmp(topic, servo_topic) == 0) {
    // Direct servo angle value (0-180)
    int servoAngle = message.toInt();
    
    // Validate servo angle range
    if (servoAngle >= 0 && servoAngle <= 180) {
      servoAngle = constrain(servoAngle, 0, 180);
      
      // Move servo to new position
      myServo.write(servoAngle);
      currentServoAngle = servoAngle;
      
      Serial.print("✓ Servo moved to: ");
      Serial.print(servoAngle);
      Serial.println("°");
      
      // Send feedback status
      String status = "Servo: " + String(servoAngle) + "°";
      client.publish(status_topic, status.c_str());
      
      // Update last message time
      lastMessage = millis();
    } else {
      Serial.print("❌ Invalid servo angle: ");
      Serial.println(servoAngle);
    }
  }
  else if (strcmp(topic, distance_topic) == 0) {
    // Finger distance value (for monitoring/debugging)
    int fingerDistance = message.toInt();
    Serial.print("📏 Finger distance: ");
    Serial.print(fingerDistance);
    Serial.println("px");
  }
  else {
    Serial.print("⚠️ Unknown topic: ");
    Serial.println(topic);
  }
}

void reconnect() {
  // Loop until we're reconnected
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    
    // Attempt to connect
    if (client.connect(client_id)) {
      Serial.println("connected");
      
      // Subscribe to multiple topics
      client.subscribe(servo_topic);
      client.subscribe(distance_topic);
      
      Serial.print("Subscribed to topics: ");
      Serial.print(servo_topic);
      Serial.print(", ");
      Serial.println(distance_topic);
      
      // Send initial status
      client.publish(status_topic, "ESP32 Servo Controller Ready");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();
  
  // Check if no message received for 5 seconds, return to center
  if (millis() - lastMessage > 5000 && currentServoAngle != 90) {
    Serial.println("No recent commands, returning servo to center position");
    myServo.write(90);
    currentServoAngle = 90;
    lastMessage = millis();
  }
  
  delay(100);  // Small delay to prevent excessive processing
}
