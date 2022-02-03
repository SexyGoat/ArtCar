//-----------------------------------------------------------------------------
// TurnCaps methods
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


#include <math.h>

#include "turncaps.h"


//-----------------------------------------------------------------------------


float TurnCaps::MaxTurnRateForSpeed(float v) {

  float omega;
  float a = max_lat_accel *
    (-1.0f + 2.0f / (1.0f + expf(-2.0f * max_turn_rate / max_lat_accel * v)));
  if (fabs(v) >= 1e-15f) {
    omega = fmax(0.0f, fmin(max_turn_rate, a / v));
  } else {
    omega = max_turn_rate;
  }
  if (reverse_turns) {
    // Reversing the vehicle preserves the direction of the turning
    // circle but reverses the sign of the rate of change of the heading.
    // (The joystick is pointed towards the turning centre.)
    omega *= (-1.0f + 2.0f / (1.0f + expf(-2.0f * reversing_omega_slope * v)));
  } else {
    // Reversing the vehicle preserves the sign of the rate of change
    // of the heading but flips the side on which the turning circle
    // appears. (RC toy tank, skid-steer. excavator, spacecraft, horse)
  }
  return omega;

}


//-----------------------------------------------------------------------------
