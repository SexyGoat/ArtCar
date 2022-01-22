//-----------------------------------------------------------------------------
// CarSpeedCtrl methods
//-----------------------------------------------------------------------------


// (c) Copyright 2022, Daniel Neville

// This file is part of ArtCar.
//
// ArtCar is free software: you can redistribute it and/or modify it
// under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// ArtCar is distributed in the hope that it will be useful, but
// WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with ArtCar. If not, see <https://www.gnu.org/licenses/>.


//-----------------------------------------------------------------------------


#include <stdint.h>
#include <math.h>

#include "carspeedctrl.h"
#include "motoracclimits.h"
#include "qposctrl.h"
#include "speedctrl.h"


//-----------------------------------------------------------------------------


CarSpeedCtrl::CarSpeedCtrl(
  const MotorAccLimits &cruise_mal,
  const MotorAccLimits &braking_mal,
  float throttle_factor,
  bool enable_throttle,
  float joy_brake_speed_threshold,
  bool enable_joy_brake
):
  SpeedCtrl(effective_mal),
  cruise_mal {cruise_mal},
  braking_mal {braking_mal},
  throttle_factor {throttle_factor},
  enable_throttle {enable_throttle},
  joy_brake_speed_threshold {joy_brake_speed_threshold},
  lever_pos {0.0f},
  input_braking_factor {0.0f},
  enable_joy_brake {enable_joy_brake},
  joy_braking_state {0}
{
  this->effective_mal = this->cruise_mal;
}


//-----------------------------------------------------------------------------


CarSpeedCtrl::CarSpeedCtrl(
  const MotorAccLimits &cruise_mal,
  const MotorAccLimits &braking_mal
): CarSpeedCtrl(
  cruise_mal,
  braking_mal,
  1.0f,
  true,
  0.2f,
  false
) {}


//-----------------------------------------------------------------------------


void CarSpeedCtrl::Animate() {

  float ts0 = this->max_speed * this->lever_pos;
  float etf = this->enable_throttle ? this->throttle_factor : 1.0f;
  float ts = this->current_speed + etf * (ts0 - this->current_speed);
  float bf = 0.0f;
  float dts = ts - this->current_speed;

  if (this->enable_joy_brake) {
    if (fabsf(this->current_speed) >= this->joy_brake_speed_threshold
        and fabsf(ts0) >= this->joy_brake_speed_threshold
        and (ts0 < 0.0f) != (this->current_speed < 0.0f)) {
      this->joy_braking_state = ts0 < 0.0f ? -1 : +1;
    }
  } else {
    this->joy_braking_state = 0;
  }

  switch (this->joy_braking_state) {
    case -1:
      if (ts0 < -this->joy_brake_speed_threshold) {
        bf = -this->lever_pos;
        ts = ts0 = fmaxf(0.0f, ts);
      } else {
        this->joy_braking_state = 0;
      }
      break;
    case +1:
      if (ts0 > this->joy_brake_speed_threshold) {
        bf = this->lever_pos;
        ts = ts0 = fminf(0.0f, ts);
      } else {
        this->joy_braking_state = 0;
      }
      break;
    default:
      break;
  }

  bf = fmaxf(bf, this->input_braking_factor);
  this->effective_braking_factor = bf;

  this->effective_mal.BlendFrom(
    this->cruise_mal,
    this->braking_mal,
    bf
  );
  ts *= (1.0f - bf);

  this->target_speed = ts;
  SpeedCtrl::Animate();

}


//-----------------------------------------------------------------------------
