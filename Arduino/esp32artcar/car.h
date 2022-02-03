//-----------------------------------------------------------------------------
// Car
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


#ifndef CAR_H_
#define CAR_H_

#include "motoracclimits.h"
#include "turncaps.h"
#include "qposctrl.h"
#include "speedctrl.h"
#include "carspeedctrl.h"


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
    const MotorAccLimits& wheel_mal,
    const MotorAccLimits& cruise_mal,
    const MotorAccLimits& braking_mal
  );
  void InitComputedValues();
};


//-----------------------------------------------------------------------------

#endif  // CAR_H_
