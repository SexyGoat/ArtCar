#ifndef SPEEDCTRL_H_
#define SPEEDCTRL_H_

#include <stdint.h>

#include "motoracclimits.h"
#include "qposctrl.h"


//-----------------------------------------------------------------------------
// Basic speed control
//-----------------------------------------------------------------------------


class SpeedCtrl {
public:
  const MotorAccLimits &mal;
  QPosCtrl _v_pos_ctrl;
  float max_speed;
  float target_speed;
  float current_speed;
  float current_accel;
  SpeedCtrl(const MotorAccLimits &motor_acc_limits);
  void ForceSpeed(float f);
  void Animate();
  void Integrate(float delta_time);
};


//-----------------------------------------------------------------------------

#endif  // SPEEDCTRL_H_
