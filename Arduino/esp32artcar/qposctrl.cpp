//-----------------------------------------------------------------------------
// QPosCtrl methods
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


#include <stdint.h>
#include <Arduino.h>

#include "qposctrl.h"


//-----------------------------------------------------------------------------


QPosCtrl::QPosCtrl(float max_fwd_v, float max_rev_v, float max_a, float x):
  max_fwd_v {max_fwd_v},
  max_rev_v {max_rev_v},
  max_a {max_a},
  target_x {x},
  x {x},
  v {0.0f}
{}


//-----------------------------------------------------------------------------


QPosCtrl::QPosCtrl():
  max_fwd_v {1.0f},
  max_rev_v {1.0f},
  max_a {1.0f},
  target_x {0.0f},
  x {0.0f},
  v {0.0f}
{}


//-----------------------------------------------------------------------------


float QPosCtrl::Integrate(float delta_time) {

  // There are five segments of the piecewise quadratic kinematic function:
  //
  // Rein - Correct any overspeeding
  // Turn - Quadratic (required to correct overshoot)
  // Lurch - Quadratic (may be projected to have a past starting point)
  // Cruise - Linear
  // Brake - Quadratic
  //
  // A dummy "Rest" piece is appended to maintain consistent execution time.
  //
  // Each function curve piece is defined by a tuple of four values:
  //   * Time (relative to "now") at the beginning of the curve;
  //   * position (x) at the beginning of the curve;
  //   * velocity, the derivative of x, at the beginning of the curve and
  //   * acceleration, the second derivative of x. for the curve.
  //
  // In general, x(t) = x0 + v0 * (t - t0) + 0.5 * a * (t - t0)**2

  float rein[4];
  float turn[4];
  float lurch[4];
  float cruise[4];
  float brake[4];
  float rest[4];

  const int TIME = 0;
  const int POS = 1;
  const int VEL = 2;
  const int ACC = 3;

  float accel = copysignf(this->max_a, v);
  float decel = -accel;

  // Rein in the current velocity if it is
  // larger than the maximum velocity.
  {
    float dv_rein = 0.0f;
    if (this->v > this->max_fwd_v) {
      dv_rein = this->max_fwd_v - this->v;
    } else if (this->v < -this->max_rev_v) {
      dv_rein = -this->max_rev_v - this->v;
    }
    const float dt_rein = fabsf(dv_rein) / this->max_a;
    const float dx_rein = (this->v + 0.5f * decel * dt_rein) * dt_rein;
    rein[TIME] = 0.0f;
    rein[POS] = this->x;
    rein[VEL] = this->v;
    rein[ACC] = decel;
    turn[TIME] = rein[TIME] + dt_rein;
    turn[POS] = rein[POS] + dx_rein;
    turn[VEL] = rein[VEL] + dv_rein;
    turn[ACC] = decel;
  }

  // Now that any overspeeding has been corrected, consider
  // (turn[TIME], turn[POS], turn[VEL]) to be the initial state.

  float t_bplurch;
  float x_bplurch;
  {
    // Find the minimum stopping time and the displacement
    // at that time if full deceleration were applied.
    const float dt_msd = fabsf(turn[VEL]) / this->max_a;
    const float dx_msd = dt_msd * (turn[VEL] + 0.5f * decel * dt_msd);
    const float t_at_msd = turn[TIME] + dt_msd;
    const float x_at_msd = turn[POS] + dx_msd;

    const int HeadingWrongWay
      = (this->target_x < turn[POS]) != (turn[VEL] < 0.0f);
    const int WillOvershootAnyway
      = (this->target_x < x_at_msd) != (dx_msd < 0.0f);

    if (HeadingWrongWay or WillOvershootAnyway) {
      // Decelerate to a stop and prepare to lurch
      // in the other direction.
      lurch[TIME] = turn[TIME] + dt_msd;
      lurch[POS] = turn[POS] + dx_msd;
      lurch[VEL] = 0.0f;
      // The back-projected time of initial rest for the
      // lurch is the same as for the beginning of the
      // lurch segment.
      t_bplurch = lurch[TIME];
      x_bplurch = lurch[POS];
    } else {
      // No turning is necessary.
      // Proceed to lurch (or lurch even more).
      lurch[TIME] = turn[TIME];
      lurch[POS] = turn[POS];
      lurch[VEL] = turn[VEL];
      t_bplurch = lurch[TIME] - dt_msd;
      x_bplurch = lurch[POS] - dx_msd;
    }
  }

  // From here on, the position is a monotonic function.
  // It is convenient to pretend that it is constant
  // or monotonically increasing.

  {
    const float dx = this->target_x - x_bplurch;
    const float max_v = dx < 0.0 ? this->max_rev_v : this->max_fwd_v;
    float accel = copysignf(this->max_a, dx);
    float decel = -accel;
    const float adx = fabsf(dx);
    const float max_dx_for_triangular_v = (max_v * max_v) / this->max_a;

    float dt_vramp;
    float dx_for_triangular_v;
    float lsd;
    float lst;
    float inflection_v;

    if (adx <= max_dx_for_triangular_v) {
      // Maximum speed not required
      dt_vramp = sqrtf(adx / this->max_a);
      dx_for_triangular_v = adx;
      lsd = 0.0f;
      lst = 0.0f;
      inflection_v = this->max_a * dt_vramp;
    } else {
      // Linear segment where maximum speed is sustained
      dt_vramp = max_v / this->max_a;
      dx_for_triangular_v = max_dx_for_triangular_v;
      lsd = adx - max_dx_for_triangular_v;
      lst = lsd / fmaxf(1e-12f, max_v);
      inflection_v = max_v;
    }

    // Acceleration
    lurch[ACC] = accel;

    // Linear segment
    cruise[TIME] = t_bplurch + dt_vramp;
    cruise[POS] = x_bplurch + 0.5f * copysign(dx_for_triangular_v, dx);
    cruise[VEL] = brake[VEL] = copysignf(inflection_v, dx);
    cruise[ACC] = 0.0f;

    // Deceleration
    brake[TIME] = cruise[TIME] + lst;
    brake[POS] = cruise[POS] + copysignf(lsd, dx);
    brake[ACC] = decel;

    // Rest
    rest[TIME] = brake[TIME] + dt_vramp;
    rest[POS] = this->target_x;
    rest[VEL] = 0.0f;
    rest[ACC] = 0.0f;
  }

  const float *qkf;
  if (delta_time < lurch[TIME]) {
    qkf = delta_time < turn[TIME] ? rein : turn;
  } else if (delta_time < brake[TIME]) {
    qkf = delta_time < cruise[TIME] ? lurch : cruise;
  } else {
    qkf = delta_time < rest[TIME] ? brake : rest;
  }
  const float t = delta_time - qkf[TIME];
  x = qkf[POS] + t * (qkf[VEL] + 0.5f * t * qkf[ACC]);
  v = qkf[VEL] + t * qkf[ACC];

  return rest[TIME];

}


//-----------------------------------------------------------------------------
