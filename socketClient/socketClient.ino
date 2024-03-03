#include "esp_camera.h"
#include <WiFi.h>
#include <ArduinoWebsockets.h>
#define CAMERA_MODEL_AI_THINKER
#include <stdio.h>
#include "camera_pins.h"
#include <ESP32Servo.h>

#define FLASH_PIN 4


const char* ssid = "WillYouProveWorthy?";  // Your wifi name like "myWifiNetwork"
const char* password = "probablynot";      // Your password to the wifi network like "password123"
const char* websocket_server_host = "192.168.2.10";
const uint16_t websocket_server_port1 = 8080;
using namespace websockets;
WebsocketsClient client;

Servo binServo, dropServo;   // create servo object to control a servo
const int binServoPin = 12;  // GPIO pin used to connect the servo control (digital out)
const int dropServoPin = 13;

const int trigPin = 15;
const int echoPin = 14;

const int bluePin = 3;
const int blackPin = 2;
const int greenPin = 1;

const int blueAngle = 0;
const int greenAngle = 80;
const int blackAngle = 170;

const int detectionThreshold = 6;  // minimum distance before triggering

int startTime;
int flashlight = 0;
int ADC_Max = 4096;

int delayBeforeDrop = 600;  //should be 1200
long duration;
int distance;

bool itemDetected() {  //add ultrasound code here

  digitalWrite(trigPin, LOW);
  delay(20);
  // Sets the trigPin on HIGH state for 10 micro seconds
  digitalWrite(trigPin, HIGH);
  delay(10);
  digitalWrite(trigPin, LOW);
  // Reads the echoPin, returns the sound wave travel time in microseconds
  duration = pulseIn(echoPin, HIGH);
  // Calculating the distance
  distance = duration * 0.034 / 2;

  if (distance < detectionThreshold) {
    return true;
  }
  return false;
}


void onEventsCallback(WebsocketsEvent event, String data) {
  if (event == WebsocketsEvent::ConnectionOpened) {
    //Serial.println("Connection Opened");
  } else if (event == WebsocketsEvent::ConnectionClosed) {
    //Serial.println("Connection Closed");
    ESP.restart();
  } else if (event == WebsocketsEvent::GotPing) {
    //Serial.println("Got a Ping!");
  } else if (event == WebsocketsEvent::GotPong) {
    //Serial.println("Got a Pong!");
  }
}

void onMessageCallback(WebsocketsMessage message) {
  String data = message.data();
  int index = data.indexOf("=");

  // Assigning Flashlight Value from server (for test purposes)
  if (index != -1) {
    String key = data.substring(0, index);
    String value = data.substring(index + 1);

    if (key == "ON_BOARD_LED_1") {
      if (value.toInt() == 1) {
        flashlight = 1;
        analogWrite(FLASH_PIN, 20);
      } else {
        flashlight = 0;
        digitalWrite(FLASH_PIN, LOW);
      }
    }

    //Serial.print("Key: ");
    //Serial.println(key);
    //Serial.print("Value: ");
    //Serial.println(value);
  } else {
    //Serial.println(data);
    //Assign servo position based on AI verdict response (STRING COMPARISON MIGHT NOT WORK AS INTENDED)
    if (data == "blue") {
      binServo.write(blueAngle);
      delay(delayBeforeDrop);
      drop();
      

    } else if (data == "green") {
      drop();

    } else if (data == "black") {
      binServo.write(blackAngle);
      delay(delayBeforeDrop);
      drop();
    }
  }
}

void sendImage(){
  camera_fb_t* fb = esp_camera_fb_get();  //Snap image
    if (!fb) {
      esp_camera_fb_return(fb);
      return;
    }
    //Serial.print("Image Captured at ");  //Debugging information
    //Serial.println(millis());
    if (fb->format != PIXFORMAT_JPEG) { return; }      // Format binary to jpeg
    client.sendBinary((const char*)fb->buf, fb->len);  //Send image

    esp_camera_fb_return(fb);
}

void drop() {  //code for controlling dropServo for dropping the item
  //open door
  delay(600);
  //close door
}
void setup() {
  //SERVO SETUP
  // Allow allocation of all timers
  ESP32PWM::allocateTimer(0);
  ESP32PWM::allocateTimer(1);
  ESP32PWM::allocateTimer(2);
  ESP32PWM::allocateTimer(3);

  binServo.setPeriodHertz(50);  // Standard 50hz servo
  //dropServo.setPeriodHertz(50);

  binServo.attach(binServoPin, 500, 2500);
  //dropServo.attach(dropServoPin,500,2500);

  binServo.write(greenAngle);

  pinMode(FLASH_PIN, OUTPUT);
  pinMode(blackPin,INPUT);
  pinMode(bluePin,INPUT);
  pinMode(greenPin,INPUT);
  //Camera Setup
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sscb_sda = SIOD_GPIO_NUM;
  config.pin_sscb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;

  config.xclk_freq_hz = 10000000;
  config.pixel_format = PIXFORMAT_JPEG;
  config.frame_size = FRAMESIZE_SVGA;
  config.jpeg_quality = 40;
  config.fb_count = 2;
  config.grab_mode = CAMERA_GRAB_LATEST;

  // camera init
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) { return; }

  sensor_t* s = esp_camera_sensor_get();

  s->set_contrast(s, 0);
  s->set_raw_gma(s, 1);

  WiFi.begin(ssid, password);
  //Serial.println("Connecting to Wifi");
  while (WiFi.status() != WL_CONNECTED) {
    //Serial.print(".");
    delay(500);
  }
  //Serial.println("Connected!");

  client.onMessage(onMessageCallback);
  client.onEvent(onEventsCallback);

  //Serial.begin(115200);
  while (!client.connect(websocket_server_host, websocket_server_port1, "/")) {
    //Serial.print(".");
    delay(500);
  }
}

void loop() {
  if (digitalRead(blackPin)) {
    analogWrite(FLASH_PIN,20);
    client.send("black");
    startTime = millis();
    //Wait for object, then capture and drop it.
    while(false){//use !itemDetected()
      if(millis()-startTime>10){client.send("timeout");return;}
    }
    sendImage();
    binServo.write(blackAngle);
    delay(delayBeforeDrop);
    drop();
    
  } else if (digitalRead(greenPin)) {
    analogWrite(FLASH_PIN,20);
    client.send("green");
    startTime = millis();
    while(false){//use !itemDetected()
      if(millis()-startTime>10){client.send("timeout");return;}
    }
    sendImage();
    drop();

  } else if (digitalRead(bluePin)) {
    analogWrite(FLASH_PIN,20);
    client.send("blue");
    startTime = millis();
    while(false){//use !itemDetected()
      if(millis()-startTime>10){client.send("timeout");return;}
    }
    sendImage();
    binServo.write(blueAngle);
    delay(delayBeforeDrop);
    drop(); 

  } else if (false) {  // ultrasound is tripped ( use itemDetected() )
    client.send("auto");
    sendImage();
    while (!client.poll()) { delay(10); }  //keep polling until the response is availible
                                           //servo control based on response is dealt with in event handler
    delay(1000);
  }
  analogWrite(FLASH_PIN,0);
  binServo.write(greenAngle);
  client.poll();  //keep connection alive by catching pings
  delay(100);
}