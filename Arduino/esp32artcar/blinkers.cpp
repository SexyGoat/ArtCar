//-----------------------------------------------------------------------------
// Blinkers methods
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
#include <Arduino.h>

#include "blinkers.h"


//-----------------------------------------------------------------------------


Blinkers::Blinkers():
  input {0},
  prev_input {0},
  state {0},
  period {830},
  on_period {415},
  phase {0},
  left_db_timer {0},
  right_db_timer {0}
{
  
}


//-----------------------------------------------------------------------------


void Blinkers::Animate() {
  const int debounce_time_ms = 70;  //ms
  const int lbit = 1;
  const int rbit = 0;
  uint8_t oldstate = this->state;
  uint8_t dbinput = this->input;
  if (dbinput & (1 << lbit)) this->left_db_timer = debounce_time_ms;
  if (dbinput & (1 << rbit)) this->right_db_timer = debounce_time_ms;
  if (this->left_db_timer) dbinput |= (1 << lbit);
  if (this->right_db_timer) dbinput |= (1 << rbit);
  uint8_t presses = dbinput & ~this->prev_input;
  this->prev_input = dbinput;
  if (presses) {
    if ((0b1001 >> this->state) & 1) {
      this->state = this->input;
    } else {
      if (this->input == 3) {
        this->state = this->input;
      } else {
        if (this->state == this->input) {
          // Do nothing.
        } else {
          this->state = 0;
        }
      }
    }
  }
  if (this->state != oldstate) {
    this->phase = 0;
  }
}


//-----------------------------------------------------------------------------


void Blinkers::Integrate_ms(int delta_time_ms) {
  this->phase += uint16_t(delta_time_ms);
  if (this->phase >= this->period) {
    this->phase -= this->period;
  }
  this->left_db_timer = uint16_t(
    max(0, int(this->left_db_timer) - delta_time_ms));
  this->right_db_timer = uint16_t(
    max(0, int(this->right_db_timer) - delta_time_ms));
}


//-----------------------------------------------------------------------------
