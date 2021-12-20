#ifndef CAR_H_
#define CAR_H_

#include "motoracclimits.h"
#include "turncaps.h"
#include "qposctrl.h"
#include "speedctrl.h"
#include "carspeedctrl.h"


//-----------------------------------------------------------------------------
// Car
//-----------------------------------------------------------------------------


class Car {
public:
  TurnCaps turn_caps;
  QPosCtrl turn_ctrl;
  CarSpeedCtrl speed_ctrl;
  SpeedCtrl lw_ctrl;
  SpeedCtrl rw_ctrl;
  float jog_factor;
  float turn_jog_factor;
  float axle_width;
  float max_wheel_speed;
  float max_body_speed;
  float max_hpat_omega;
  Car(
    const MotorAccLimits &wheel_mal,
    const MotorAccLimits &cruise_mal,
    const MotorAccLimits &braking_mal
  );
  void InitComputedValues();
};


//-----------------------------------------------------------------------------

#endif  // CAR_H_
