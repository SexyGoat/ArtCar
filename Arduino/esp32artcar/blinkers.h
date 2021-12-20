#ifndef BLINKERS_H_
#define BLINKERS_H_

#include <stdint.h>


//-----------------------------------------------------------------------------
// Blinkers (direction indicators)
//-----------------------------------------------------------------------------


class Blinkers {
public:
  uint8_t input;  // Bit 1 = Left, bit 0 = Right
  uint8_t prev_input;
  uint8_t state;  // Bit 1 = Left, bit 0 = Right
  uint16_t period;
  uint16_t on_period;
  uint16_t phase;
  uint16_t left_db_timer;
  uint16_t right_db_timer;
  Blinkers();
  void Animate();
  void Integrate_ms(int delta_time_ms);
};


//-----------------------------------------------------------------------------

#endif  // BLINKERS_H_
