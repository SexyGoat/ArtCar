#ifndef ANIMATECAR_H_
#define ANIMATECAR_H_
//-----------------------------------------------------------------------------
// Animation (and integration) of Car and General Control State
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


#include "gcstate.h"
#include "inputstate.h"
#include "joycal.h"
#include "car.h"


//-----------------------------------------------------------------------------
// Animation (and integration) of Car and General Control State
//-----------------------------------------------------------------------------


void AnimateGCSAndCar(
  GeneralCtrlState& gcs,
  InputState& inp,
  GamepadCal& gpcal,
  Car& car
);


//-----------------------------------------------------------------------------


void IntegrateGCSAndCar(
  GeneralCtrlState& gcs,
  Car& car,
  float delta_time
);


//-----------------------------------------------------------------------------

#endif  // ANIMATECAR_H_
