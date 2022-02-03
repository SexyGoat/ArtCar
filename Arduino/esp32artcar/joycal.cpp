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
#include <Arduino.h>

#include "joycal.h"
#include "inputstate.h"


//-----------------------------------------------------------------------------


uint8_t JoyAxisMidSlop(JoyAxisCal& axis_cal) {
  return uint8_t(
    (uint16_t(axis_cal.slop_low) + uint16_t(axis_cal.slop_high)) >> 1
  );
}


//-----------------------------------------------------------------------------


float JoyAxis2Float(uint8_t x, const JoyAxisCal& axis_cal) {
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


void InitGamepadCalibration(GamepadCal& gpcal) {

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


void CalibrateAxis(
  JoyAxisCal& calibration,
  uint8_t value,
  const JoyAxisCal& thresholds,
  JoyAxisCalState& state,
  uint16_t delta_time_ms
) {

  const uint16_t slop_time_threshold = 500;  // milliseconds
  
  if (not state.floating) {
    state.slop_time_ms = 0;
    if (value < thresholds.low or value > thresholds.high) {
      state.floating = true;
      calibration.low = value;
      calibration.high = value;
    }
  }
  if (state.floating) {
    if (value < calibration.low) calibration.low = value;
    if (value > calibration.high) calibration.high = value;
    if (value >= thresholds.slop_low and value <= thresholds.slop_high) {
      if (state.slop_time_ms < slop_time_threshold) {
        calibration.slop_low = value;
        calibration.slop_high = value;
      }
      state.slop_time_ms += delta_time_ms;
      state.slop_time_ms = min(state.slop_time_ms, slop_time_threshold);
      if (state.slop_time_ms >= slop_time_threshold) {
        if (value < calibration.slop_low) calibration.slop_low = value;
        if (value > calibration.slop_high) calibration.slop_high = value;
      }
    } else {
      state.slop_time_ms = 0;
    }
    
  }
}


//-----------------------------------------------------------------------------


void CalibrateGamepad(
  GamepadCal& calibration,
  const InputState& input,
  GamepadCalState& state,
  uint16_t delta_time_ms
) {

  const JoyAxisCal joy_thresholds = {
    .low = 64,
    .high = 192,
    .slop_low = 96,
    .slop_high = 160,
  };
  const JoyAxisCal trigger_thresholds = {
    .low = 0,
    .high = 128,
    .slop_low = 0,
    .slop_high = 64,
  };

  CalibrateAxis(
    calibration.leftx,
    input.leftx,
    joy_thresholds,
    state.leftx,
    delta_time_ms
  );
  CalibrateAxis(
    calibration.lefty,
    input.lefty,
    joy_thresholds,
    state.lefty,
    delta_time_ms
  );
  CalibrateAxis(
    calibration.rightx,
    input.rightx,
    joy_thresholds,
    state.rightx,
    delta_time_ms
  );
  CalibrateAxis(
    calibration.righty,
    input.righty,
    joy_thresholds,
    state.righty,
    delta_time_ms
  );
  CalibrateAxis(
    calibration.lefttrigger,
    input.lefttrigger,
    trigger_thresholds,
    state.lefttrigger,
    delta_time_ms
  );
  CalibrateAxis(
    calibration.righttrigger,
    input.righttrigger,
    trigger_thresholds,
    state.righttrigger,
    delta_time_ms
  );
  
}


//-----------------------------------------------------------------------------
