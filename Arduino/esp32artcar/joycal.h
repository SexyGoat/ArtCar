#ifndef JOYCAL_H_
#define JOYCAL_H_

#include <stdint.h>


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
// Joystick functions
//-----------------------------------------------------------------------------


uint8_t JoyAxisMidSlop(JoyAxisCal &axis_cal);
float JoyAxis2Float(uint8_t x, const JoyAxisCal &axis_cal);
void InitGamepadCalibration(GamepadCal &gpcal);


//-----------------------------------------------------------------------------

#endif  // JOYCAL_H_
