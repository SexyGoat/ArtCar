#include <stdint.h>
#include <Arduino.h>

#include "blinkers.h"


//-----------------------------------------------------------------------------
// Blinkers methods
//-----------------------------------------------------------------------------


Blinkers::Blinkers():
  input {0},
  prev_input {0},
  state {0},
  period {830},
  on_period {415},
  phase {0},
  left_db_timer {0},
  right_db_timer {0}
{
  
}


//-----------------------------------------------------------------------------


void Blinkers::Animate() {
  const int debounce_time_ms = 70;  //ms
  const int lbit = 1;
  const int rbit = 0;
  uint8_t oldstate = this->state;
  uint8_t dbinput = this->input;
  if (dbinput & (1 << lbit)) this->left_db_timer = debounce_time_ms;
  if (dbinput & (1 << rbit)) this->right_db_timer = debounce_time_ms;
  if (this->left_db_timer) dbinput |= (1 << lbit);
  if (this->right_db_timer) dbinput |= (1 << rbit);
  uint8_t presses = dbinput & ~this->prev_input;
  this->prev_input = dbinput;
  if (presses) {
    if ((0b1001 >> this->state) & 1) {
      this->state = this->input;
    } else {
      if (this->input == 3) {
        this->state = this->input;
      } else {
        if (this->state == this->input) {
          // Do nothing.
        } else {
          this->state = 0;
        }
      }
    }
  }
  if (this->state != oldstate) {
    this->phase = 0;
  }
}


//-----------------------------------------------------------------------------


void Blinkers::Integrate_ms(int delta_time_ms) {
  this->phase += uint16_t(delta_time_ms);
  if (this->phase >= this->period) {
    this->phase -= this->period;
  }
  this->left_db_timer = uint16_t(
    max(0, int(this->left_db_timer) - delta_time_ms));
  this->right_db_timer = uint16_t(
    max(0, int(this->right_db_timer) - delta_time_ms));
}


//-----------------------------------------------------------------------------
