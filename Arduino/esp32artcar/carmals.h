#ifndef CARMALS_H_
#define CARMALS_H_

#include <stdint.h>

#include "motoracclimits.h"


//-----------------------------------------------------------------------------
// Car motor acceleration limits
//-----------------------------------------------------------------------------


typedef struct {
  MotorAccLimits wheel_mal;
  MotorAccLimits cruise_mal;
  MotorAccLimits braking_mal;
} CarMALs;


//-----------------------------------------------------------------------------

#endif  // CARMALS_H_
