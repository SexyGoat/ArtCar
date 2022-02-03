#ifndef CARSPEEDCTRL_H_
#define CARSPEEDCTRL_H_
//-----------------------------------------------------------------------------
// Car speed control
//-----------------------------------------------------------------------------


// (c) Copyright 2022, Daniel Neville

// This file is part of ArtCar.
//
// ArtCar is free software: You can redistribute it and/or modify it
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

#include "speedctrl.h"
#include "motoracclimits.h"


//-----------------------------------------------------------------------------


class CarSpeedCtrl: public SpeedCtrl {
protected:
  MotorAccLimits effective_mal;
public:
  const MotorAccLimits& cruise_mal;
  const MotorAccLimits& braking_mal;
  float throttle_factor;
  float joy_brake_speed_threshold;
  float lever_pos;
  float input_braking_factor;
  bool enable_throttle;
  float effective_braking_factor;
  bool enable_joy_brake;
  int8_t joy_braking_state;
  CarSpeedCtrl(
    const MotorAccLimits& cruise_mal,
    const MotorAccLimits& braking_mal,
    float throttle_factor,
    bool enable_throttle,
    float joy_brake_speed_threshold,
    bool enable_joy_brake
  );
  CarSpeedCtrl(
    const MotorAccLimits& cruise_mal,
    const MotorAccLimits& braking_mal
  );
  void Animate();
};


//-----------------------------------------------------------------------------

#endif  // CARSPEEDCTRL_H_
