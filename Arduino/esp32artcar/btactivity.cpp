//-----------------------------------------------------------------------------
// BTActivity methods
//-----------------------------------------------------------------------------


// (c) Copyright 2021, Daniel Neville

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

#include "btactivity.h"


//-----------------------------------------------------------------------------


void BTActivity::Animate() {

  switch (state) {
    case 1: {
      this->activity_ms = 0;
      this->activity_counter = 0;
      this->lamp_state = ((this->phase >> 7) & 7) == 0;
      break;
    }
    case 2: {
      if (this->activity_ms > 0) {
        this->activity_counter = (this->activity_counter + 1) & 7;
      } else {
        this->activity_counter = 0;
      }
      this->lamp_state = this->activity_counter == 0;
      break;
    }
    default: {
      this->phase = 0;
      this->activity_ms = 0;
      this->activity_counter = 0;
      this->lamp_state = 0;
      break;
    }
  }
  
}


//-----------------------------------------------------------------------------


void BTActivity::Integrate_ms(int delta_time_ms) {

  this->activity_ms = uint8_t(max(0, int(activity_ms) - delta_time_ms));
  this->phase = (this->phase + uint16_t(delta_time_ms)) & 0x3FF;
  
}


//-----------------------------------------------------------------------------
