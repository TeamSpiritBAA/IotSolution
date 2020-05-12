#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <TinyGPS++.h>
#include <SoftwareSerial.h>
#include <DHT.h>;

#define DHTPIN 4 //D2
#define DHTTYPE DHT22
#ifndef STASSID
#define STASSID "SSID"
#define STAPSK "Password"
#endif

DHT dht(DHTPIN, DHTTYPE);
TinyGPSPlus gps;

const char* ssid = STASSID;
const char* password = STAPSK;
const char* mqtt_broker = "test.mosquitto.org";

static const int RXPin = 13, TXPin = 15 ;
static const uint32_t GPSBaud = 9600;
SoftwareSerial ss(RXPin, TXPin);

float lumValue = 0;

WiFiClient espClient;
PubSubClient mqttClient(espClient);
long lastMsg = 0;
char msg[100];

void setup(void) {
  Serial.begin(9600);
  dht.begin();
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  Serial.println("");
  ss.begin(GPSBaud);

  // Wait for connection
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.print("Connected to ");
  Serial.println(ssid);
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());

  //MQTT:
  mqttClient.setServer(mqtt_broker, 1883);
  mqttClient.setCallback(callback);
}

  void callback(char* topic, byte* payload, unsigned int length) {
    Serial.print("Topic: [");
    Serial.print(topic);
    Serial.print("]");
    Serial.print(" payload:");
    for (int i=0;i<length; i++){
      Serial.print((char)payload[i]);
    }
    if ((char)payload[0] == '1') {
      Serial.println(" correct");
    }else{
      Serial.println(" wrong");
    }
  }
 
void reconnect(){
  while(!mqttClient.connected()){
    Serial.print("Attempting MQTT connection ");
    String clientID = "ESP8266Client-";
    clientID += String(random(0xffff),HEX);

    if(mqttClient.connect(clientID.c_str())){
        Serial.println("connected ");
        mqttClient.subscribe("UniqueID");
    }else{
      Serial.print("Failed, rc=");
      Serial.print(mqttClient.state());
      Serial.println(" retrying...");
      delay(5000);
    }
  }
}
void loop(void) {
  if(!mqttClient.connected()){
    reconnect();
  }
  mqttClient.loop(); 
  while (ss.available() > 0){
      gps.encode(ss.read());
    } 
  long now = millis();
  if(now-lastMsg > 5000){
    lastMsg = now;
    lumValue = analogRead(A0);
    if(lumValue < 100){
      Serial.println("no light detected, entering power saving mode");
      ESP.deepSleep(30e6);
    }else{
      float hum = dht.readHumidity();
      float temp = dht.readTemperature();
      float xcoor = gps.location.lng();
      float ycoor = gps.location.lat();
      snprintf (msg,100, "T%f,H%f,X%f,Y%f,L%f",temp,hum,xcoor,ycoor,lumValue);
      mqttClient.publish("IDDeniss/esptest",msg);
    }
  }
}

// Just Testing
