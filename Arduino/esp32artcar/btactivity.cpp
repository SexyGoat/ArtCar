#include <stdint.h>
#include <Arduino.h>

#include "btactivity.h"


//-----------------------------------------------------------------------------
// BTActivity methods
//-----------------------------------------------------------------------------


void BTActivity::Animate() {

  switch (state) {
    case 1: {
      this->activity_ms = 0;
      this->activity_counter = 0;
      this->lamp_state = ((this->phase >> 7) & 7) == 0;
      break;
    }
    case 2: {
      if (this->activity_ms > 0) {
        this->activity_counter = (this->activity_counter + 1) & 7;
      } else {
        this->activity_counter = 0;
      }
      this->lamp_state = this->activity_counter == 0;
      break;
    }
    default: {
      this->phase = 0;
      this->activity_ms = 0;
      this->activity_counter = 0;
      this->lamp_state = 0;
      break;
    }
  }
  
}


//-----------------------------------------------------------------------------


void BTActivity::Integrate_ms(int delta_time_ms) {

  this->activity_ms = uint8_t(max(0, int(activity_ms) - delta_time_ms));
  this->phase = (this->phase + uint16_t(delta_time_ms)) & 0x3FF;
  
}


//-----------------------------------------------------------------------------
