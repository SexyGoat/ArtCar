#ifndef BLINKERS_H_
#define BLINKERS_H_
//-----------------------------------------------------------------------------
// Blinkers (direction indicators)
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


//-----------------------------------------------------------------------------


class Blinkers {
public:
  uint8_t input;  // Bit 1 = Left, bit 0 = Right
  uint8_t prev_input;
  uint8_t state;  // Bit 1 = Left, bit 0 = Right
  uint16_t period;
  uint16_t on_period;
  uint16_t phase;
  uint16_t left_db_timer;
  uint16_t right_db_timer;
  Blinkers();
  void Animate();
  void Integrate_ms(int delta_time_ms);
};


//-----------------------------------------------------------------------------

#endif  // BLINKERS_H_
