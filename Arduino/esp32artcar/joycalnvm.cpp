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
#include <string.h>

#include <Arduino.h>
#include <Preferences.h>

#include "joycalnvm.h"
#include "joycal.h"


//-----------------------------------------------------------------------------


Preferences preferences;


//-----------------------------------------------------------------------------
// JoyCalKeeper methods
//-----------------------------------------------------------------------------


int JoyCalKeeper::FindSlotByMAC(uint8_t mac48[6]) {

  int result = -1;
  
  bool exists = preferences.begin("multigpcal", true);
  if (exists) {

    int i;
    char slot_name[] = "gpcal_slot_x";
    uint8_t slot_buf[31];
  
    for (i = 0; i < this->num_slots; ++i) {
      slot_name[sizeof(slot_name) - 2] = '0' + i;
      if (preferences.isKey(slot_name)) {
        preferences.getBytes(slot_name, slot_buf, sizeof(slot_buf));
        if (memcmp(mac48, slot_buf + 1, 6) == 0) {
          // A match!
          result = i;
          break;
        }
      }
    }
  
    preferences.end();
    
  }
  
  return result;

}


//-----------------------------------------------------------------------------

  
void JoyCalKeeper::LoadSlot(int slot_index, JoyNMVSlot& slot_to_load) {

  bool exists = preferences.begin("multigpcal", true);
  if (exists) {

    char slot_name[] = "gpcal_slot_x";
    uint8_t slot_buf[31];
    const int gpc = 7;
  
    slot_name[sizeof(slot_name) - 2] = '0' + slot_index;
    if (preferences.isKey(slot_name)) {
      preferences.getBytes(slot_name, slot_buf, sizeof(slot_buf));
      slot_to_load.seq_num = slot_buf[0];
      memcpy(slot_to_load.mac48, slot_buf + 1, 6);
      slot_to_load.gamepad_cal.leftx.low = slot_buf[gpc + 0];
      slot_to_load.gamepad_cal.leftx.high = slot_buf[gpc + 1];
      slot_to_load.gamepad_cal.leftx.slop_low = slot_buf[gpc + 2];
      slot_to_load.gamepad_cal.leftx.slop_high = slot_buf[gpc + 3];
      slot_to_load.gamepad_cal.lefty.low = slot_buf[gpc + 4];
      slot_to_load.gamepad_cal.lefty.high = slot_buf[gpc + 5];
      slot_to_load.gamepad_cal.lefty.slop_low = slot_buf[gpc + 6];
      slot_to_load.gamepad_cal.lefty.slop_high = slot_buf[gpc + 7];
      slot_to_load.gamepad_cal.rightx.low = slot_buf[gpc + 8];
      slot_to_load.gamepad_cal.rightx.high = slot_buf[gpc + 9];
      slot_to_load.gamepad_cal.rightx.slop_low = slot_buf[gpc + 10];
      slot_to_load.gamepad_cal.rightx.slop_high = slot_buf[gpc + 11];
      slot_to_load.gamepad_cal.righty.low = slot_buf[gpc + 12];
      slot_to_load.gamepad_cal.righty.high = slot_buf[gpc + 13];
      slot_to_load.gamepad_cal.righty.slop_low = slot_buf[gpc + 14];
      slot_to_load.gamepad_cal.righty.slop_high = slot_buf[gpc + 15];
      slot_to_load.gamepad_cal.lefttrigger.low = slot_buf[gpc + 16];
      slot_to_load.gamepad_cal.lefttrigger.high = slot_buf[gpc +17];
      slot_to_load.gamepad_cal.lefttrigger.slop_low = slot_buf[gpc + 18];
      slot_to_load.gamepad_cal.lefttrigger.slop_high = slot_buf[gpc + 19];
      slot_to_load.gamepad_cal.righttrigger.low = slot_buf[gpc + 20];
      slot_to_load.gamepad_cal.righttrigger.high = slot_buf[gpc +21];
      slot_to_load.gamepad_cal.righttrigger.slop_low = slot_buf[gpc + 22];
      slot_to_load.gamepad_cal.righttrigger.slop_high = slot_buf[gpc + 23];
    }
  
    preferences.end();
    
  }
  
}


//-----------------------------------------------------------------------------

  
int JoyCalKeeper::SaveSlot(int slot_index, JoyNMVSlot& slot_to_save) {

  preferences.begin("multigpcal");

  char slot_name[] = "gpcal_slot_x";
  uint8_t slot_buf[31];

  int index_to_use;
  uint8_t sqn_to_use = slot_to_save.seq_num;

  if (slot_index >= 0 and slot_index < this->num_slots) {
    index_to_use = slot_index;
    slot_name[sizeof(slot_name) - 2] = '0' + index_to_use;
    if (preferences.isKey(slot_name)) {
      preferences.getBytes(slot_name, slot_buf, sizeof(slot_buf));
      sqn_to_use = slot_buf[0];
    }
  } else {
    index_to_use = -1;
    bool found_a_slot = false;
    uint8_t prev_sqn = 255;
    uint8_t sqn;
    uint8_t expected_sqn;
    for (int i = 0; i < this->num_slots; ++i) {
      expected_sqn = (prev_sqn + 1) & 255;
      slot_name[sizeof(slot_name) - 2] = '0' + i;
      if (preferences.isKey(slot_name)) {
        preferences.getBytes(slot_name, slot_buf, sizeof(slot_buf));
        sqn = slot_buf[0];
        if (not found_a_slot) {
          found_a_slot = true;
        } else {
          if (sqn != expected_sqn) {
            index_to_use = i;
            break;
          }
        }
        prev_sqn = sqn;
      } else {
        // A hole! It must be filled!
        index_to_use = i;
        break;
      }
      if (index_to_use < 0) {
        // Discontinuity only at array bounds.
        index_to_use = 0;
        expected_sqn = (prev_sqn + 1) & 255;
      }
    }
    sqn_to_use = expected_sqn;
  }

  const int gpc = 7;

  slot_to_save.seq_num = sqn_to_use;
  slot_buf[0] = sqn_to_use;
  memcpy(slot_buf + 1, slot_to_save.mac48, 6);
  slot_buf[gpc + 0] = slot_to_save.gamepad_cal.leftx.low;
  slot_buf[gpc + 1] = slot_to_save.gamepad_cal.leftx.high;
  slot_buf[gpc + 2] = slot_to_save.gamepad_cal.leftx.slop_low;
  slot_buf[gpc + 3] = slot_to_save.gamepad_cal.leftx.slop_high;
  slot_buf[gpc + 4] = slot_to_save.gamepad_cal.lefty.low;
  slot_buf[gpc + 5] = slot_to_save.gamepad_cal.lefty.high;
  slot_buf[gpc + 6] = slot_to_save.gamepad_cal.lefty.slop_low;
  slot_buf[gpc + 7] = slot_to_save.gamepad_cal.lefty.slop_high;
  slot_buf[gpc + 8] = slot_to_save.gamepad_cal.rightx.low;
  slot_buf[gpc + 9] = slot_to_save.gamepad_cal.rightx.high;
  slot_buf[gpc + 10] = slot_to_save.gamepad_cal.rightx.slop_low;
  slot_buf[gpc + 11] = slot_to_save.gamepad_cal.rightx.slop_high;
  slot_buf[gpc + 12] = slot_to_save.gamepad_cal.righty.low;
  slot_buf[gpc + 13] = slot_to_save.gamepad_cal.righty.high;
  slot_buf[gpc + 14] = slot_to_save.gamepad_cal.righty.slop_low;
  slot_buf[gpc + 15] = slot_to_save.gamepad_cal.righty.slop_high;
  slot_buf[gpc + 16] = slot_to_save.gamepad_cal.lefttrigger.low;
  slot_buf[gpc + 17] = slot_to_save.gamepad_cal.lefttrigger.high;
  slot_buf[gpc + 18] = slot_to_save.gamepad_cal.lefttrigger.slop_low;
  slot_buf[gpc + 19] = slot_to_save.gamepad_cal.lefttrigger.slop_high;
  slot_buf[gpc + 20] = slot_to_save.gamepad_cal.righttrigger.low;
  slot_buf[gpc + 21] = slot_to_save.gamepad_cal.righttrigger.high;
  slot_buf[gpc + 22] = slot_to_save.gamepad_cal.righttrigger.slop_low;
  slot_buf[gpc + 23] = slot_to_save.gamepad_cal.righttrigger.slop_high;

  slot_name[sizeof(slot_name) - 2] = '0' + index_to_use;
  preferences.putBytes(slot_name, slot_buf, sizeof(slot_buf));

  preferences.end();

  return index_to_use;
  
}


//-----------------------------------------------------------------------------
