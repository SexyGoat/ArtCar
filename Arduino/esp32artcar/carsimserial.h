#ifndef CARSIMSERIAL_H_
#define CARSIMSERIAL_H_
//-----------------------------------------------------------------------------
// Serial output for controlling the Pygame car simulator from the ESP32
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


#include "inputstate.h"
#include "car.h"
#include "gcstate.h"
#include "blinkers.h"


//-----------------------------------------------------------------------------


void SetArtCarSimStateStr(
  char (&buf8z)[9],
  InputState& inp,
  Car& car,
  GeneralCtrlState& gcs,
  Blinkers& blinkers
);


//-----------------------------------------------------------------------------

#endif  // CARSIMSERIAL_H_
