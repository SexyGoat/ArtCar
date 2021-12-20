#include <Arduino.h>
#include <stdint.h>

#include "virtualio.h"
#include "bitfiddling.h"


//-----------------------------------------------------------------------------
// Virtual output pins
//-----------------------------------------------------------------------------


void WritePin(bool logical_state, const VOPin &vo_desc) {
  bool state = (logical_state ^ vo_desc.sense) & 1;
  switch (vo_desc.drive_mode) {
    case kVOutputDriveSink:
      digitalWrite(vo_desc.arduino_pin, state);
      break;
    case kVOutputDriveOnly:
      if (state) {
        pinMode(vo_desc.arduino_pin, OUTPUT);
        digitalWrite(vo_desc.arduino_pin, 1);
      } else {
        pinMode(vo_desc.arduino_pin, INPUT);
      }
      break;
    case kVOutputSinkOnly:
      if (state) {
        pinMode(vo_desc.arduino_pin, INPUT);
      } else {
        pinMode(vo_desc.arduino_pin, OUTPUT);
        digitalWrite(vo_desc.arduino_pin, 0);
      }
      break;
    case kVOutputWPUSink:
      if (state) {
        pinMode(vo_desc.arduino_pin, INPUT_PULLUP);
      } else {
        pinMode(vo_desc.arduino_pin, OUTPUT);
        digitalWrite(vo_desc.arduino_pin, 0);
      }
      break;
    default:
      break;
  }
}


//-----------------------------------------------------------------------------


void WritePins(uint32_t vo_states, const VOPin vo_array[], int vo_count) {
  int i;
  for (i = 0; i < vo_count; i++) {
    WritePin((vo_states >> i) & 1, vo_array[i]);
  }
}


//-----------------------------------------------------------------------------


void ConfigPin(bool logical_state, const VOPin &vo_desc) {
  if (vo_desc.drive_mode == kVOutputDriveSink) {
    pinMode(vo_desc.arduino_pin, OUTPUT);
  }
  // It turns out that most of the configuration work
  // is performed in the pin output function.
  WritePin(logical_state, vo_desc);
}


//-----------------------------------------------------------------------------


void ConfigPins(uint32_t vo_states, const VOPin vo_array[], int vo_count) {
  int i;
  for (i = 0; i < vo_count; i++) {
    ConfigPin((vo_states >> i) & 1, vo_array[i]);
  }
}


//-----------------------------------------------------------------------------
