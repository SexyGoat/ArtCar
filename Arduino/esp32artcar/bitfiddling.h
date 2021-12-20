#ifndef BITFIDDLING_H_
#define BITFIDDLING_H_

#include <stdint.h>


//-----------------------------------------------------------------------------
// Bit fiddling functions
//-----------------------------------------------------------------------------


bool FetchBit(uint32_t mask, int bit_pos);
uint32_t WriteBit(uint32_t mask, int bit_pos, bool bit_value);


//-----------------------------------------------------------------------------

#endif  // BITFIDDLING_H_
