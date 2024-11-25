#include <Adafruit_PWMServoDriver.h>
#include <WiFi.h>
#include <WebServer.h>

// Wi-Fi credentials
const char* ssid = "raspit";
const char* password = "raspit1ras";

WebServer server(80); 

Adafruit_PWMServoDriver board1 = Adafruit_PWMServoDriver(0x40);       // called this way, it uses the default address 0x40   

#define SERVOMIN  125                                                 // this is the 'minimum' pulse length count (out of 4096)
#define SERVOMAX  625                                                 // this is the 'maximum' pulse length count (out of 4096)

int val, mapped_val;    // variable to read the value from the analog pin
String logMsg; 


int angleToPulse(int ang)                             //gets angle in degree and returns the pulse width
  {  int pulse = map(ang,0, 180, SERVOMIN,SERVOMAX);  // map angle of 0 to 180 to Servo min and Servo max 
     Serial.print("Angle: ");Serial.print(ang);
     Serial.print(" pulse: ");Serial.println(pulse);
     return pulse;
  }

void setup() {
  Serial.begin(115200);
  Serial.println("16 channel Servo test!");
  board1.begin();
  board1.setPWMFreq(60);                  // Analog servos run at ~60 Hz updates

  // Connect to Wi-Fi
  WiFi.begin(ssid, password);
  Serial.println("Connecting to Wi-Fi...");
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println(".");
  }
  delay(6000);
  Serial.println("Connected to Wi-Fi");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());

    // Handle servo control
  server.on("/setServo", []() {
    String value = server.arg("value");
    int servo_no = server.arg("id").toInt();
    int angle = value.toInt();
    
    if (angle >= -45 && angle <= 225) {
      mapped_val = map(angle, -45, 225, 0, 180);     // scale it for use with the servo library (value between 0 and 180)

      board1.setPWM(servo_no-1, 0, angleToPulse(angle) );

      // servos[servo_no-1].write(mapped_val);  // Set servo position
      Serial.println("Servo angle set to: " + String(angle));
      server.sendHeader("Access-Control-Allow-Origin", "*");
      server.send(200, "text/plain", "OK");
    } else {
      server.sendHeader("Access-Control-Allow-Origin", "*");
      server.send(400, "text/plain", "Invalid Angle");
    }
  });

  server.begin();  // Start the server
  Serial.println("Server started");
}

void loop() 
  { 
    server.handleClient();  // Handle client requests

    // int i = 0;
    // board1.setPWM(i, 0, angleToPulse(0) );
    // Serial.println("111");
    
    // delay(1000);
    // board1.setPWM(i, 0, angleToPulse(90) );
    // Serial.println("222");
    
    // delay(1000);
    // board1.setPWM(i, 0, angleToPulse(180) );
    // Serial.println("333");
    
    // delay(1000);
    // board1.setPWM(i, 0, angleToPulse(90) );
    // Serial.println("444");
  }
