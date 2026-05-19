volatile int count = 0;//if the interrupt will change this value, it must be volatile

void setup() {
 pinMode(2, INPUT);
 digitalWrite(2, HIGH);
 attachInterrupt(digitalPinToInterrupt(34), interruptName, RISING);
// attachInterrupt(digitalPinToInterrupt(39), interruptName, RISING);
 Serial.begin(9600);
}

// vp - 36
// vn - 39

void loop() {
  Serial.println(count);//see the counts advance
  delay(100);//Delays usually can't be interfered with, here we will see the interrupt work
}//end loop

void interruptName()
{
  count = count+1;
}
