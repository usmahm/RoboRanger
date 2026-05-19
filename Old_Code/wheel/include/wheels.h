#pragma once

#include "Arduino.h"

struct WHEEL
{
  const int IN1;
  const int IN2;
  const int EN;
  
  WHEEL(int IN1, int  IN2, int EN);

  void initialize();

  void set_velocity(double velocity);
};

namespace WHEELS {
  extern WHEEL w_1;
  extern WHEEL w_2;

  extern WHEEL w_3;
  extern WHEEL w_4;
}
