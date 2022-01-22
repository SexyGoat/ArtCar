#ifndef BTACTIVITY_H_
#define BTACTIVITY_H_
//-----------------------------------------------------------------------------
// Bluetooth connection and activity
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


class BTActivity {
public:
  uint8_t activity_ms;
  uint8_t state: 3;  // 0: Off, 1:Searching, 2:Connected
  uint8_t activity_counter: 3;  // Keeps the LED from going fully dark.
  uint8_t lamp_state: 1;
  uint16_t phase;
  void Animate();
  void Integrate_ms(int delta_time_ms);
};


//-----------------------------------------------------------------------------

#endif  // BTACTIVITY_H_
