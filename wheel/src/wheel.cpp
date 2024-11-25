#include "wheel.h"

WHEEL::WHEEL(int IN1, int IN2, int EN) : IN1(IN1), IN2(IN2), EN(EN) {};

void WHEEL::initialize() {
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(EN, OUTPUT);

  setVelocity(0); // Stop motors initially
}

void WHEEL::setVelocity(double velocity) {
  bool forward = true;
  int pwm_value = 0;
  double max_velocity = 10.0;

  if (velocity < 0) {
    forward = false;
    pwm_value = constrain(-velocity * 255 / max_velocity, 0, 255);
  } else {
    pwm_value = constrain(velocity * 255 / max_velocity, 0, 255);
  }

  digitalWrite(IN1, forward ? HIGH : LOW);
  digitalWrite(IN2, forward ? LOW : HIGH);

  Serial.println(pwm_value);

  analogWrite(EN, pwm_value);
}