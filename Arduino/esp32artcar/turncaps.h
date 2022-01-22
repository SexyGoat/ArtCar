#ifndef TURNCAPS_H_
#define TURNCAPS_H_
//-----------------------------------------------------------------------------
// Turning capabilities
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


#include <Arduino.h> // for DEG_TO_RAD


//-----------------------------------------------------------------------------


class TurnCaps {
public:
  float max_lat_accel = 4.0f;  // in m/s^2: 1.47m/s^2 standard for highways.
  float max_turn_rate = 90.0f * DEG_TO_RAD;  // in rad/s
  float reversing_omega_slope = 1.0f;  // For stick-to-turn-centre mode
  bool reverse_turns = false;  // Stick-to-turn-centre mode (car-like)
  float MaxTurnRateForSpeed(float v);
};


//-----------------------------------------------------------------------------

#endif  // TURNCAPS_H_
