#ifndef ANIMATECAR_H_
#define ANIMATECAR_H_

#include "gcstate.h"
#include "inputstate.h"
#include "joycal.h"
#include "car.h"


//-----------------------------------------------------------------------------
// Animation (and integration) of Car and General Control State
//-----------------------------------------------------------------------------


void AnimateGCSAndCar(
  GeneralCtrlState &gcs,
  InputState &inp,
  GamepadCal &gpcal,
  Car &car
);


//-----------------------------------------------------------------------------


void IntegrateGCSAndCar(
  GeneralCtrlState &gcs,
  Car &car,
  float delta_time
);


//-----------------------------------------------------------------------------

#endif  // ANIMATECAR_H_
