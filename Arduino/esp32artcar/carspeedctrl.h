#ifndef CARSPEEDCTRL_H_
#define CARSPEEDCTRL_H_

#include <stdint.h>

#include "speedctrl.h"
#include "motoracclimits.h"


//-----------------------------------------------------------------------------
// Car speed control
//-----------------------------------------------------------------------------


class CarSpeedCtrl: public SpeedCtrl {
protected:
  MotorAccLimits effective_mal;
public:
  const MotorAccLimits &cruise_mal;
  const MotorAccLimits &braking_mal;
  float throttle_factor;
  float joy_brake_speed_threshold;
  float lever_pos;
  float input_braking_factor;
  bool enable_throttle;
  float effective_braking_factor;
  bool enable_joy_brake;
  int8_t joy_braking_state;
  CarSpeedCtrl(
    const MotorAccLimits &cruise_mal,
    const MotorAccLimits &braking_mal,
    float throttle_factor,
    bool enable_throttle,
    float joy_brake_speed_threshold,
    bool enable_joy_brake
  );
  CarSpeedCtrl(
    const MotorAccLimits &cruise_mal,
    const MotorAccLimits &braking_mal
  );
  void Animate();
};


//-----------------------------------------------------------------------------

#endif  // CARSPEEDCTRL_H_
