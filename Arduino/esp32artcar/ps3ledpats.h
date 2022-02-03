#ifndef PS3LEDPATS_H_
#define PS3LEDPATS_H_
//-----------------------------------------------------------------------------
// PS3 LED patterns
//-----------------------------------------------------------------------------


// (c) Copyright 2022, Daniel Neville

// This file is part of ArtCar.
//
// ArtCar is free software: You can redistribute it and/or modify it
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


#define kLEDPatMilliseconds 1250


//-----------------------------------------------------------------------------


enum {
  kLEDPat_BattLevel4 = 10,  // 1111
  kLEDPat_BattLevel3 = 9,   // 1110
  kLEDPat_BattLevel2 = 7,   // 1100
  kLEDPat_BattLevel1 = 4,   // 1000
  kLEDPat_JoyISO = 3,       // 0100
  kLEDPat_JoyVH = 8,        // 1101
  kLEDPat_JoyModHPat = 6,   // 1010
  kLEDPat_JoyHPat = 5,      // 1001
  kLEDPat_Slow = 1,         // 0001
  kLEDPat_Fast = 2,         // 0010
};

enum {
  kLEDPatDispIx_Batt = 0,
  kLEDPatDispIx_Layout,
  kLEDPatDispIx_Speed,
  kLEDPatDispIx_NumItems,
};


//-----------------------------------------------------------------------------

#endif  // PS3LEDPATS_H_
