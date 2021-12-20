#include <stdint.h>

#include "car.h"


//-----------------------------------------------------------------------------
// Car methods
//-----------------------------------------------------------------------------


Car::Car(
  const MotorAccLimits &wheel_mal,
  const MotorAccLimits &cruise_mal,
  const MotorAccLimits &braking_mal
):
  speed_ctrl {cruise_mal, braking_mal},
  lw_ctrl {wheel_mal},
  rw_ctrl {wheel_mal},
  jog_factor {0.25f},
  turn_jog_factor {0.25f},
  axle_width {1.0f},
  max_wheel_speed {1.0f},
  max_body_speed {1.0f},
  max_hpat_omega {1.0f} // Probably way off. It will be computed.
{}


//-----------------------------------------------------------------------------


void Car::InitComputedValues() {

  this->max_hpat_omega = 2.0f * this->max_wheel_speed / this->axle_width;
  this->turn_caps.max_turn_rate = fminf(
    this->turn_caps.max_turn_rate, this->max_hpat_omega
  );

  bool mbs_too_high = true;
  float omega;
  float hds;
  float new_max_body_speed;
  while (mbs_too_high) {
    mbs_too_high = false;
    omega = this->turn_caps.MaxTurnRateForSpeed(this->max_body_speed);
    hds = 0.5f * omega * this->axle_width;
    if (this->max_body_speed + hds > this->max_wheel_speed) {
      new_max_body_speed = this->max_wheel_speed - hds;
      if (new_max_body_speed < this->max_body_speed) {
        this->max_body_speed = new_max_body_speed;
        mbs_too_high = true;
      }
    }
  }
  
}


//-----------------------------------------------------------------------------
