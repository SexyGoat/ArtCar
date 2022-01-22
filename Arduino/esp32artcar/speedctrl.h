#ifndef SPEEDCTRL_H_
#define SPEEDCTRL_H_
//-----------------------------------------------------------------------------
// Basic speed control
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

#include "motoracclimits.h"
#include "qposctrl.h"


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
