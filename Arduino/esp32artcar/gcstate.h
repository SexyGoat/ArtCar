#ifndef GCSTATE_H_
#define GCSTATE_H_

#include <stdint.h>


//-----------------------------------------------------------------------------
// General control state flags and trimming flags
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
  kJoystickHPat,
};


//-----------------------------------------------------------------------------
// Main state structure
//-----------------------------------------------------------------------------


typedef struct {
  int idm;
  GCFlags flags;
  float max_trim;
  float trim;
  float trim_vel;
} GeneralCtrlState;


//-----------------------------------------------------------------------------

#endif  // GCSTATE_H_
