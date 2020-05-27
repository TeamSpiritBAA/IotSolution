#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <TinyGPS++.h>
#include <SoftwareSerial.h>
#include <DHT.h>;

#define DHTPIN 4 //D2 pin on the ESP
#define DHTTYPE DHT22 //change in accordance to your sensor
#ifndef STASSID
#define STASSID "SSID" //change to match yours
#define STAPSK "PASSWORD"
#endif

DHT dht(DHTPIN, DHTTYPE);
TinyGPSPlus gps;

const char* ssid = STASSID;
const char* password = STAPSK;
const char* mqtt_broker = "mqtt.eclipse.org"; //change to match your broker

static const int RXPin = 13, TXPin = 15 ; // D7 & D6 on the ESP
static const uint32_t GPSBaud = 9600;
SoftwareSerial ss(RXPin, TXPin);

float lumValue = 0;
WiFiClient espClient;
PubSubClient mqttClient(espClient);
long lastMsg = 0;
char msg[100];
int sleeptime;

//behaviour on startup
void setup(void) {
  //initializing sensors and wifi
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
  //Function for handling incoming MQTT payload
  void callback(char* topic, byte* payload, unsigned int length) {
    Serial.print("Topic: [");
    Serial.print(topic);
    Serial.print("]");
    Serial.print(" payload:");
    for (int i=0;i<length; i++){
      Serial.print((char)payload[i]);
    }
    if ((char)payload[0] == 'S') {
      Serial.println("Entering manual sleep mode..");
      sleeptime = (int)payload[1] * 36e8; //example: payload S2 = enter sleep mode for 2 hours
      ESP.deepSleep(sleeptime); 
      ;
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
      Serial.println("retrying...");
      delay(5000);
    }
  }
}

int calculateLum(float Value){
  float realVolts = Value*3.3/1024;
  float LDResistance = (3.3-realVolts)*10/realVolts;
  int LUX = 500/LDResistance;
  return LUX;
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
  if(now-lastMsg > 3e5){ //every 5 minutes, adjust as needed
    lastMsg = now;
    float sensorValue = analogRead(A0);
    lumValue = calculateLum(sensorValue);
    if(lumValue < 50){
      Serial.println("no light detected, entering power saving mode");
      ESP.deepSleep(12e8); //20 minutes in microseconds
    }else{
      float hum = dht.readHumidity();
      float temp = dht.readTemperature();
      float xcoor = gps.location.lng();
      float ycoor = gps.location.lat();
      snprintf (msg,100, "T%f,H%f,X%f,Y%f,L%f",temp,hum,xcoor,ycoor,lumValue); //saving into one data string
      mqttClient.publish("IDDeniss/esptest",msg);
    }
  }
}
