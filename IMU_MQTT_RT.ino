#include <SPI.h>
#include <Arduino_LSM6DS3.h>
#include <ArduinoJson.h>
#include <PubSubClient.h>
#include <WiFiNINA.h>
//==================================================================
//==================================================================
//// Wifi
const char* ssid = "Nmail_0U";
const char* password = "isnl74269";

//// Topic 
const char publishTopic[] = "nmail/";


//==================================================================
//==================================================================
bool isStart = false;

void setup_wifi();

static char payload[256];

//"mqtt.pumpkinhouse.io" is a mqtt serverar
// const char mqtt_server[] = "mqtt.pumpkinhouse.io";
const char mqtt_server[] = "143.248.143.21";
const char mqtt_password[] = "74269";
const char mqtt_username[] = "nmail";

float reset_time;
WiFiClient wifiClient;
PubSubClient mqtt(wifiClient);
//--------------------------------------------------------------------------
void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);

  while ( WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  randomSeed(micros());
  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());

}

void reconnect() {
  while (!mqtt.connected()) {
    Serial.print("Attempting MQTT connection ....");
    String clientID = "Collar-";
    clientID += String(random(0xffff), HEX);

    if (mqtt.connect(clientID.c_str(), mqtt_username, mqtt_password)) {   
      Serial.println("Connected to MQTT Broker");
    }
    else
    {
      Serial.print("failed, rc=");
      Serial.print(mqtt.state());
      Serial.println("try again in 5 second");
    }
  }
}
//==================================================================================
void setup() {
  Serial.begin(115200);

  if (!IMU.begin())
  {
    Serial.println("Failed to initialize IMU!");
    while (1);
  }
  setup_wifi();
  mqtt.setServer(mqtt_server, 1883);
}

//==================================================================================
void loop() {
  if (!mqtt.connected())
  {
    reconnect();
  }

  mqtt.loop();
  
    StaticJsonDocument<1024> doc;
    JsonObject root = doc.to<JsonObject>();
    JsonObject IMU_data = root["imu"].to<JsonObject>();

    float start_time, end_time, wifi_time;

    wifi_time = micros();
    start_time = wifi_time;


    float aX, aY, aZ;
    float gX, gY, gZ;
    if (IMU.accelerationAvailable() && IMU.gyroscopeAvailable()) {
      IMU.readAcceleration(aX, aY, aZ);
      IMU.readGyroscope(gX, gY, gZ);
      IMU_data["aX"] = aX;
      IMU_data["aY"] = aY;
      IMU_data["aZ"] = aZ;
      IMU_data["gX"] = gX;
      IMU_data["gY"] = gY;
      IMU_data["gZ"] = gZ;

    }
    serializeJsonPretty(doc, payload);
    mqtt.publish(publishTopic, payload);
    Serial.println(payload);
    end_time = micros();
    while ( (end_time - wifi_time) < 50000) { //Wifi : 20Hz 50000
      end_time = micros();
    }
  


}
