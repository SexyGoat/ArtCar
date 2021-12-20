#include <stdint.h>

#include "bitfiddling.h"


//-----------------------------------------------------------------------------
// Bit fiddling functions
//-----------------------------------------------------------------------------


bool FetchBit(uint32_t mask, int bit_pos) {
  return bool((mask >> bit_pos) & 1);
}


//-----------------------------------------------------------------------------


uint32_t WriteBit(uint32_t mask, int bit_pos, bool bit_value) {
  uint32_t bm = 1 << bit_pos;
  if (bit_value) {
    return mask | bm;
  } else {
    return mask & ~bm;
  }
}


//-----------------------------------------------------------------------------
