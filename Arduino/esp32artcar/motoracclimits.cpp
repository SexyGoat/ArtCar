//-----------------------------------------------------------------------------
// MotorAccLimits methods
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


#include "motoracclimits.h"
#include "lerpf.h"


//-----------------------------------------------------------------------------


MotorAccLimits::MotorAccLimits(
  float facc,
  float fdec,
  float racc,
  float rdec,
  float jerk
):
  max_fwd_accel {facc},
  max_fwd_decel {fdec},
  max_rev_accel {racc},
  max_rev_decel {rdec},
  max_jerk {jerk}
{
  
}


//-----------------------------------------------------------------------------


MotorAccLimits::MotorAccLimits(float accel, float jerk): MotorAccLimits(
  accel, accel, accel, accel, jerk
) {}


//-----------------------------------------------------------------------------


MotorAccLimits::MotorAccLimits():
  MotorAccLimits(1.0f, 1.0f)
{}


//-----------------------------------------------------------------------------


void MotorAccLimits::BlendFrom(
  const MotorAccLimits &mal1,
  const MotorAccLimits &mal2,
  float t
) {
  this->max_fwd_accel = Lerpf(mal1.max_fwd_accel, mal2.max_fwd_accel, t);
  this->max_fwd_decel = Lerpf(mal1.max_fwd_decel, mal2.max_fwd_decel, t);
  this->max_rev_accel = Lerpf(mal1.max_rev_accel, mal2.max_rev_accel, t);
  this->max_rev_decel = Lerpf(mal1.max_fwd_decel, mal2.max_rev_decel, t);
  this->max_jerk = Lerpf(mal1.max_jerk, mal2.max_jerk, t);
}


//-----------------------------------------------------------------------------
