#ifndef GCSTATE_H_
#define GCSTATE_H_
//-----------------------------------------------------------------------------
// General control state flags and trimming flags
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


//-----------------------------------------------------------------------------


typedef struct {
  uint8_t use_alt_ctrl_method: 1;
  uint8_t reverse_turns: 1;
  uint8_t limit_turn_rate: 1;
  uint8_t enable_joy_brake: 1;
  uint8_t soften_speed: 1;
  uint8_t soften_turns: 1;
  uint8_t soften_throttle: 1;
  uint8_t motors_are_magic: 1;
  uint8_t trimming: 1;
  uint8_t zeroing_trim: 1;
  uint8_t stop_lamp: 1;
  uint8_t reversing_lamp: 1;
  uint8_t enable_motors: 1;
} GCFlags;


//-----------------------------------------------------------------------------
// Input device mode
//-----------------------------------------------------------------------------


enum {
  kJoystickISO,
  kJoystickVH,
  kJoystickModHPat,
  kJoystickHPat,
};


//-----------------------------------------------------------------------------
// Main state structure
//-----------------------------------------------------------------------------


typedef struct {
  int idm;
  float pwm_scaler;
  GCFlags flags;
  float max_trim;
  float trim;
  float trim_vel;
} GeneralCtrlState;


//-----------------------------------------------------------------------------

#endif  // GCSTATE_H_
