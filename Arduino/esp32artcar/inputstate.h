#ifndef INPUTSTATE_H_
#define INPUTSTATE_H_

#include <stdint.h>

#include <Ps3Controller.h>


//-----------------------------------------------------------------------------
// Input state (of PS3 controller)
//-----------------------------------------------------------------------------


typedef struct {
  uint8_t leftx;
  uint8_t lefty;
  uint8_t rightx;
  uint8_t righty;
  uint8_t lefttrigger;
  uint8_t righttrigger;
  ps3_button_t buttons;
} InputState;


//-----------------------------------------------------------------------------

#endif  // INPUTSTATE_H_
