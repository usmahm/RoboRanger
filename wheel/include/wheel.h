#pragma once

#include "Arduino.h"

struct WHEEL
{
  const int IN1;
  const int IN2;
  const int EN;
  
  WHEEL(int IN1, int  IN2, int EN);

  void initialize();

  void setVelocity(double velocity);
};
