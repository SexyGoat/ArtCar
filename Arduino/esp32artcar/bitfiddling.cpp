//-----------------------------------------------------------------------------
// Bit fiddling functions
//-----------------------------------------------------------------------------


// (c) Copyright 2022, Daniel Neville

// This file is part of ArtCar.
//
// ArtCar is free software: you can redistribute it and/or modify it
// under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// ArtCar is distributed in the hope that it will be useful, but
// WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with ArtCar. If not, see <https://www.gnu.org/licenses/>.


//-----------------------------------------------------------------------------


#include <stdint.h>

#include "bitfiddling.h"


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
