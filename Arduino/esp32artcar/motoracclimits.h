#ifndef MOTORACCLIMITS_H_
#define MOTORACCLIMITS_H_
//-----------------------------------------------------------------------------
// Motor Acceleration Limits
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


class MotorAccLimits {
public:
  float max_fwd_accel;
  float max_fwd_decel;
  float max_rev_accel;
  float max_rev_decel;
  float max_jerk;
  MotorAccLimits(float facc, float fdec, float racc, float rdec, float jerk);
  MotorAccLimits(float accel, float jerk);
  MotorAccLimits();
  void BlendFrom(
    const MotorAccLimits& mal1,
    const MotorAccLimits& mal2,
    float t
  );
};


//-----------------------------------------------------------------------------

#endif  // MOTORACCLIMITS_H_
