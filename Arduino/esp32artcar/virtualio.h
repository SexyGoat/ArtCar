#ifndef VIRTUALIO_H_
#define VIRTUALIO_H_
//-----------------------------------------------------------------------------
// Virtual output pins
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


enum {
  kVOSenseActiveHigh = 0,
  kVOSenseActiveLow = 1,
};

enum {
  kVOutputDriveSink,
  kVOutputWPUSink,
  kVOutputDriveOnly,
  kVOutputSinkOnly,
};

typedef struct {
  int8_t vo_index;
  int8_t arduino_pin;
  int8_t sense;
  int8_t drive_mode;
} VOPin;


//-----------------------------------------------------------------------------


void ConfigPin(bool logical_state, const VOPin &vo_desc);
void ConfigPins(uint32_t vo_states, const VOPin vo_array[], int vo_count);
void WritePin(bool logical_state, const VOPin &vo_desc);
void WritePins(uint32_t vo_states, const VOPin vo_array[], int vo_count);


//-----------------------------------------------------------------------------

#endif  // VIRTUALIO_H_
