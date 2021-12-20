#ifndef VIRTUALIO_H_
#define VIRTUALIO_H_

#include <stdint.h>


//-----------------------------------------------------------------------------
// Virtual output pins
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
