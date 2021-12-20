#ifndef TURNCAPS_H_
#define TURNCAPS_H_

#include <Arduino.h> // for DEG_TO_RAD


//-----------------------------------------------------------------------------
// Turning capabilities
//-----------------------------------------------------------------------------


class TurnCaps {
public:
  float max_lat_accel = 4.0f;  // in m/s^2: 1.47m/s^2 standard for highways.
  float max_turn_rate = 90.0f * DEG_TO_RAD;  // in rad/s
  float reversing_omega_slope = 1.0f;  // For stick-to-turn-centre mode
  bool reverse_turns = false;  // Stick-to-turn-centre mode (car-like)
  float MaxTurnRateForSpeed(float v);
};


//-----------------------------------------------------------------------------

#endif  // TURNCAPS_H_
