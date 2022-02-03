#ifndef INPUTSTATE_H_
#define INPUTSTATE_H_
//-----------------------------------------------------------------------------
// Input state (of PS3 controller)
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

#include <Ps3Controller.h>


//-----------------------------------------------------------------------------


typedef struct {
  uint8_t leftx;
  uint8_t lefty;
  uint8_t rightx;
  uint8_t righty;
  uint8_t lefttrigger;
  uint8_t righttrigger;
  ps3_button_t buttons;
} InputState;


//-----------------------------------------------------------------------------

#endif  // INPUTSTATE_H_
