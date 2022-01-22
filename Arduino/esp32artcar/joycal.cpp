//-----------------------------------------------------------------------------
// Gamepad calibration
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

#include <stdint.h>

#include "joycal.h"


//-----------------------------------------------------------------------------


uint8_t JoyAxisMidSlop(JoyAxisCal &axis_cal) {
  return uint8_t(
    (uint16_t(axis_cal.slop_low) + uint16_t(axis_cal.slop_high)) >> 1
  );
}


//-----------------------------------------------------------------------------


float JoyAxis2Float(uint8_t x, const JoyAxisCal &axis_cal) {
  float r = 0.0f;
  const JoyAxisCal c = axis_cal;
  x = constrain(x, c.low, c.high);
  if (x > c.slop_high and c.slop_high < c.high) {
    float slop_high_f = float(c.slop_high);
    r = (float(x) - slop_high_f) / (float(c.high) - slop_high_f);
  } else if (x < c.slop_low and c.slop_low > c.low) {
    float slop_low_f = float(c.slop_low);
    r = (float(x) - slop_low_f) / (slop_low_f - float(c.low));
  }
  return r;
}


//-----------------------------------------------------------------------------


void InitGamepadCalibration(GamepadCal &gpcal) {

  const JoyAxisCal default_joy_axis_cal = {
    .low = 0,
    .high = 255,
    .slop_low = 120,
    .slop_high = 134,
  };

  const JoyAxisCal default_trigger_axis_cal = {
    .low = 0,
    .high = 255,
    .slop_low = 0,
    .slop_high = 10,
  };

  gpcal.leftx = default_joy_axis_cal;
  gpcal.lefty = default_joy_axis_cal;
  gpcal.rightx = default_joy_axis_cal;
  gpcal.righty = default_joy_axis_cal;
  gpcal.lefttrigger = default_trigger_axis_cal;
  gpcal.righttrigger = default_trigger_axis_cal;

}


//-----------------------------------------------------------------------------
