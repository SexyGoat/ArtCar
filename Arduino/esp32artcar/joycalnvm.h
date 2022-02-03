#ifndef JOYCALNVM_H_
#define JOYCALNVM_H_
//-----------------------------------------------------------------------------
// Gamepad calibration saved to non-volatile memory
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
#include <Preferences.h>

#include "joycal.h"


//-----------------------------------------------------------------------------
// Fun stuff
//-----------------------------------------------------------------------------


typedef struct {
  uint8_t seq_num;
  uint8_t mac48[6];
  GamepadCal gamepad_cal;
} JoyNMVSlot;


//-----------------------------------------------------------------------------


class JoyCalKeeper {
public:
  static const int num_slots = 4;
  int FindSlotByMAC(uint8_t mac48[6]);
  void LoadSlot(int slot_index, JoyNMVSlot& slot_to_load);
  int SaveSlot(int slot_index, JoyNMVSlot& slot_to_save);
};


//-----------------------------------------------------------------------------
// Joy!
//-----------------------------------------------------------------------------


//bool MacExists



//-----------------------------------------------------------------------------

#endif  // JOYCALNVM_H_
