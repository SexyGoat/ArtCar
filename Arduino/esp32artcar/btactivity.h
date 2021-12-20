#ifndef BTACTIVITY_H_
#define BTACTIVITY_H_

#include <stdint.h>


//-----------------------------------------------------------------------------
// Bluetooth connection and activity
//-----------------------------------------------------------------------------


class BTActivity {
public:
  uint8_t activity_ms;
  uint8_t state: 3;  // 0: Off, 1:Searching, 2:Connected
  uint8_t activity_counter: 3;  // Keeps the LED from going fully dark.
  uint8_t lamp_state: 1;
  uint16_t phase;
  void Animate();
  void Integrate_ms(int delta_time_ms);
};


//-----------------------------------------------------------------------------

#endif  // BTACTIVITY_H_
