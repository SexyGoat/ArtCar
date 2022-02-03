#ifndef JOYCAL_H_
#define JOYCAL_H_
//-----------------------------------------------------------------------------
// Gamepad calibration
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

#include "inputstate.h"


//-----------------------------------------------------------------------------
// Joystick axis calibration
//-----------------------------------------------------------------------------


typedef struct {
  uint8_t low;
  uint8_t high;
  uint8_t slop_low;
  uint8_t slop_high;
} JoyAxisCal;


//-----------------------------------------------------------------------------
// Gamepad calibration
//-----------------------------------------------------------------------------


typedef struct {
  JoyAxisCal leftx;
  JoyAxisCal lefty;
  JoyAxisCal rightx;
  JoyAxisCal righty;
  JoyAxisCal lefttrigger;
  JoyAxisCal righttrigger;
} GamepadCal;


//-----------------------------------------------------------------------------
// Joystick axis calibration state, used during the calibration procedure
//-----------------------------------------------------------------------------


typedef struct {
  uint16_t slop_time_ms: 15;
  bool floating: 1;
} JoyAxisCalState;


//-----------------------------------------------------------------------------
// Gamepad calibration state, used during the calibration procedure
//-----------------------------------------------------------------------------


typedef struct {
  JoyAxisCalState leftx;
  JoyAxisCalState lefty;
  JoyAxisCalState rightx;
  JoyAxisCalState righty;
  JoyAxisCalState lefttrigger;
  JoyAxisCalState righttrigger;
} GamepadCalState;


//-----------------------------------------------------------------------------
// Joystick functions
//-----------------------------------------------------------------------------


uint8_t JoyAxisMidSlop(JoyAxisCal& axis_cal);
float JoyAxis2Float(uint8_t x, const JoyAxisCal& axis_cal);

void InitGamepadCalibration(GamepadCal& gpcal);

void CalibrateAxis(
  JoyAxisCal& calibration,
  uint8_t value,
  const JoyAxisCal& thresholds,
  JoyAxisCalState& state,
  uint16_t delta_time_ms
);

void CalibrateGamepad(
  GamepadCal& calibration,
  const InputState& input,
  GamepadCalState& state,
  uint16_t delta_time_ms
);


//-----------------------------------------------------------------------------

#endif  // JOYCAL_H_
