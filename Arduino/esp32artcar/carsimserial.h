#ifndef CARSIMSERIAL_H_
#define CARSIMSERIAL_H_

#include "inputstate.h"
#include "car.h"
#include "gcstate.h"
#include "blinkers.h"


//-----------------------------------------------------------------------------
// Serial output for controlling the Pygame car simulator from the ESP32
//-----------------------------------------------------------------------------


void SetArtCarSimStateStr(
  char (&buf8z)[9],
  InputState &inp,
  Car &car,
  GeneralCtrlState &gcs,
  Blinkers &blinkers
);


//-----------------------------------------------------------------------------

#endif  // CARSIMSERIAL_H_
