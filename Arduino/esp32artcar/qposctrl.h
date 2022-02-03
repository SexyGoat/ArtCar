#ifndef QPOSCTRL_H_
#define QPOSCTRL_H_
//-----------------------------------------------------------------------------
// Quadratic Position Controller
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


class QPosCtrl {
public:
  float max_fwd_v;
  float max_rev_v;
  float max_a;
  float target_x;
  float x;
  float v;
  QPosCtrl(float max_fwd_v, float max_rev_v, float max_a, float x);
  QPosCtrl();
  float Integrate(float delta_time);
};


//-----------------------------------------------------------------------------

#endif  // QPOSCTRL_H_
