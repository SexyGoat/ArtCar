#include <stdint.h>

#include "carsimserial.h"

#include "inputstate.h"
#include "car.h"
#include "gcstate.h"
#include "blinkers.h"


//-----------------------------------------------------------------------------
// Serial output for ArtCarSim
//-----------------------------------------------------------------------------


char Tricrumb2Base64(uint8_t tricrumb) {
  uint8_t x = tricrumb & 63;
  char r;
  if (x < 52) {
    if (x < 26) {
      r = x + 'A';
    } else {
      r = x - 26 + 'a';
    }
  } else {
    if (x < 62) {
      r = x - 52 + '0';
    } else {
      r = x == 62 ? '+' : '/';
    }
  }
  return r;
}


//-----------------------------------------------------------------------------


void Int2Base64(char (&buf6)[6], int32_t x) {
  uint32_t u;
  if (x >= 0) {
    u = uint32_t(x);
  } else {
    u = 0xFFFFFFFFu - uint32_t(-(x + 1));
  }
  for (int i = 6; i--; ) {
    buf6[i] = Tricrumb2Base64(uint8_t(u & 63));
    u >>= 6;
  }
}


//-----------------------------------------------------------------------------


void SetArtCarSimStateStr(
  char (&buf8z)[9],
  InputState &inp,
  Car &car,
  GeneralCtrlState &gcs,
  Blinkers &blinkers
) {

  char B[6];
  int x;
  x = (0
    | (inp.buttons.cross << 0)      // a
    | (inp.buttons.circle << 1)     // b
    | (inp.buttons.triangle << 2)   // y
    | (inp.buttons.square << 3)     // x
    | (inp.buttons.l1 << 4)         // leftshoulder
    | (inp.buttons.r1 << 5)         // rightshoulder
    | (inp.buttons.l2 << 6)         // lefttrigger
    | (inp.buttons.r2 << 7)         // righttrigger
    | (inp.buttons.select << 8)     // back ("CREATE" on PS5)
    | (inp.buttons.start << 9)      // start (hamburger on PS5)
    | (inp.buttons.ps << 10)        // guide
    | (inp.buttons.l3 << 11)        // leftstick
    | (inp.buttons.r3 << 12)        // rightstick
    | (inp.buttons.up << 13)        // dpad_up
    | (inp.buttons.down << 14)      // dpad_down
    | (inp.buttons.left << 15)      // dpad_left
    | (inp.buttons.right << 16)     // dpad_right
  );
  Int2Base64(B, x);
  buf8z[0] = B[3];
  buf8z[1] = B[4];
  buf8z[2] = B[5];
  x = (0
    | (gcs.flags.reversing_lamp << 3)
    | (gcs.flags.stop_lamp << 2)
    | ((blinkers.phase < blinkers.on_period ? blinkers.state : 0b00) << 0)
  );
  Int2Base64(B, x);
  buf8z[3] = B[5];
  float k = 2047.0f / car.max_wheel_speed;
  x = int32_t(k * car.lw_ctrl.target_speed + 0.5f);
  Int2Base64(B, constrain(x, -2047, +2047));
  buf8z[4] = B[4];
  buf8z[5] = B[5];
  x = int32_t(k * car.rw_ctrl.target_speed + 0.5f);
  Int2Base64(B, constrain(x, -2047, +2047));
  buf8z[6] = B[4];
  buf8z[7] = B[5];
  buf8z[8] = '\x00';

}


//-----------------------------------------------------------------------------
