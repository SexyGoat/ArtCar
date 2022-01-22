#ifndef CARMALS_H_
#define CARMALS_H_
//-----------------------------------------------------------------------------
// Car motor acceleration limits
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


//-----------------------------------------------------------------------------


typedef struct {
  MotorAccLimits wheel_mal;
  MotorAccLimits cruise_mal;
  MotorAccLimits braking_mal;
} CarMALs;


//-----------------------------------------------------------------------------

#endif  // CARMALS_H_
