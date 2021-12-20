#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt


def sgn2(x):
  return -1 if x < 0 else 1


def linspace_step(start, end, approx_step, endpoint=True):
  n = max(2, int(np.rint((end - start) / approx_step))) if end > start else 1
  result = np.linspace(start, end, n, endpoint=endpoint)
  return result


class QPosCtrl (object):

  def __init__(self):
    self.x = 0.0
    self.v = 0.0
    self.target_x = 0.0
    self.max_fwd_v = 1e6
    self.max_rev_v = 1e6
    self.max_a = 1e6
    self.integral = 0.0

  def animate(self, delta_time):

    # There are five segments of the piecewise quadratic kinematic function:
    #
    # Rein - Correct any overspeeding
    # Turn - Quadratic (required to correct overshoot)
    # Lurch - Quadratic (may be projected to have a past starting point)
    # Cruise - Linear
    # Brake - Quadratic
    #
    # A dummy "Rest" piece is appended to maintain consistent execution time.
    #
    # Each function curve piece is defined by a tuple of four values:
    #   * Time (relative to "now") at the beginning of the curve;
    #   * position (x) at the beginning of the curve;
    #   * velocity, the derivative of x, at the beginning of the curve and
    #   * acceleration, the second derivative of x. for the curve.
    #
    # In general, x(t) = x0 + v0 * (t - t0) + 0.5 * a * (t - t0)**2

    rein = np.zeros([4])
    turn = np.zeros([4])
    lurch = np.zeros([4])
    cruise = np.zeros([4])
    brake = np.zeros([4])
    rest = np.zeros([4])

    TIME = 0
    POS = 1
    VEL = 2
    ACC = 3

    accel = np.copysign(self.max_a, self.v)
    decel = -accel

    # Rein in the current velocity if it is
    # larger than the maximum velocity.
    dv_rein = 0.0
    if self.v > self.max_fwd_v:
      dv_rein = self.max_fwd_v - self.v
    elif self.v < -self.max_rev_v:
      dv_rein = -self.max_rev_v - self.v
    dt_rein = abs(dv_rein) / self.max_a
    dx_rein = (self.v + 0.5 * decel * dt_rein) * dt_rein
    rein[TIME] = 0.0
    rein[POS] = self.x
    rein[VEL] = self.v
    rein[ACC] = decel
    turn[TIME] = rein[TIME] + dt_rein
    turn[POS] = rein[POS] + dx_rein
    turn[VEL] = rein[VEL] + dv_rein
    turn[ACC] = decel

    # Now that any overspeeding has been corrected, consider
    # (turn[TIME], turn[POS], turn[VEL]) to be the initial state.

    # Find the minimum stopping time and the displacement
    # at that time if full deceleration were applied.
    dt_msd = abs(turn[VEL]) / self.max_a
    dx_msd = dt_msd * (turn[VEL] + 0.5 * dt_msd * decel)
    t_at_msd = turn[TIME] + dt_msd
    x_at_msd = turn[POS] + dx_msd

    HeadingWrongWay = (self.target_x < turn[POS]) != (turn[VEL] < 0)
    WillOvershootAnyway = (self.target_x < x_at_msd) != (dx_msd < 0.0)

    if HeadingWrongWay or WillOvershootAnyway:
      # Decelerate to a stop and prepare to lurch
      # in the other direction.
      lurch[TIME] = turn[TIME] + dt_msd
      lurch[POS] = turn[POS] + dx_msd
      lurch[VEL] = 0.0
      # The back-projected time of initial rest for the
      # lurch is the same as for the beginning of the
      # lurch segment.
      t_bplurch = lurch[TIME]
      x_bplurch = lurch[POS]
    else:
      # No turning is necessary.
      # Proceed to lurch (or lurch even more).
      lurch[TIME] = turn[TIME]
      lurch[POS] = turn[POS]
      lurch[VEL] = turn[VEL]
      t_bplurch = lurch[TIME] - dt_msd
      x_bplurch = lurch[POS] - dx_msd

    # From here on, the position is a monotonic function.
    # It is convenient to pretend that it is constant
    # or monotonically increasing.
    dx = self.target_x - x_bplurch
    adx = abs(dx)
    accel = np.copysign(self.max_a, dx)
    decel = -accel
    max_v = self.max_rev_v if dx <= 0.0 else self.max_fwd_v
    max_dx_for_triangular_v = (max_v * max_v) / self.max_a

    if adx <= max_dx_for_triangular_v:
      # Maximum speed not required
      dt_vramp = np.sqrt(adx / self.max_a)
      dx_for_triangular_v = adx
      lsd = 0.0
      lst = 0.0
      inflection_v = self.max_a * dt_vramp
    else:
      # Linear segment where maximum speed is sustained
      dt_vramp = max_v / self.max_a
      dx_for_triangular_v = max_dx_for_triangular_v
      lsd = adx - max_dx_for_triangular_v
      lst = lsd / max(1e-12, max_v)
      inflection_v = max_v

    # Acceleration
    lurch[ACC] = accel

    # Linear segment
    cruise[TIME] = t_bplurch + dt_vramp
    cruise[POS] = x_bplurch + 0.5 * np.copysign(dx_for_triangular_v, dx)
    cruise[VEL] = brake[VEL] = np.copysign(inflection_v, dx)
    cruise[ACC] = 0.0

    # Deceleration
    brake[TIME] = cruise[TIME] + lst
    brake[POS] = cruise[POS] + np.copysign(lsd, dx)
    brake[ACC] = decel

    # Rest
    rest[TIME] = brake[TIME] + dt_vramp
    rest[POS] = self.target_x
    rest[VEL] = 0.0
    rest[ACC] = 0.0

    qkfs = (rein, turn, lurch, cruise, brake, rest)

    # Evaluate the piecewise quadratic function at t = dt.
    if delta_time < lurch[TIME]:
      if delta_time < turn[TIME]:
        qkf_ix = 0  # rein
      else:
        qkf_ix = 1  # turn
    elif delta_time < brake[TIME]:
      if delta_time < cruise[TIME]:
        qkf_ix = 2  # lurch
      else:
        qkf_ix = 3  # cruise
    else:
      if delta_time < rest[TIME]:
        qkf_ix = 4  # brake
      else:
        qkf_ix = 5  # rest

    # Bonus feature: x is integrated.
    for i in range(0, qkf_ix + 1):
      t1 = qkfs[i + 1][TIME] if i + 1 < len(qkfs) else t0 + delta_time
      if t1 >= 0.0:
        qkf = qkfs[i]
        t0 = qkf[TIME]
        x0 = qkf[POS]
        v0 = qkf[VEL]
        a = qkf[ACC]
        if t0 < 0:
          x0 += (0.5 * a * t0 - v0) * t0
          v0 -= a * t0
        sdt = min(delta_time, t1) - t0
        self.integral += sdt * (x0 + sdt * (0.5 * v0 + sdt * (1.0/6.0) * a))

    qkf = qkfs[qkf_ix]

    t = delta_time - qkf[TIME]
    # Horner's method avoids raising small numbers to high powers
    # and halves the number of multiplications needed to evaluate
    # a polynomial.
    self.x = qkf[POS] + t * (qkf[VEL] + 0.5 * t * qkf[ACC])
    self.v = qkf[VEL] + t * qkf[ACC]


def main():

  params = {
    (0, 0): dict(
      title = "From Rest to Rest",
      x0 = -1.0,
      x1 = 1.5,
      v0 = 0.0,
      max_a = 5.0,
      max_fwd_v = 3.0,
      max_rev_v = 3.0,
    ),
    (0, 1): dict(
      title = "Below Top Speed",
      x0 = -1.0,
      x1 = 3.5,
      v0 = 1.5,
      max_a = 3.0,
      max_fwd_v = 3.5,
      max_rev_v = 3.5,
    ),
    (1, 0): dict(
      title = "Already at Top Speed",
      x0 = 1.5,
      x1 = -2.0,
      v0 = -4.0,
      max_a = 4.0,
      max_fwd_v = 4.0,
      max_rev_v = 4.0,
    ),
    (1, 1): dict(
      title = "Overshoot",
      x0 = -0.5,
      x1 = 0.5,
      v0 = 3.5,
      max_a = 3.0,
      max_fwd_v = 3.5,
      max_rev_v = 3.5,
    ),
    (2, 0): dict(
      title = "Overspeed",
      x0 = 1.5,
      x1 = -2.0,
      v0 = -4.0,
      max_a = 4.0,
      max_fwd_v = 2.0,
      max_rev_v = 2.0,
    ),
    (2, 1): dict(
      title = "Overspeed, Overshoot",
      x0 = -0.5,
      x1 = 0.5,
      v0 = 5.5,
      max_a = 3.0,
      max_fwd_v = 3.5,
      max_rev_v = 3.5,
    ),
  }

  plot_step = 0.005

  fig = plt.figure(constrained_layout=True)
  axs = fig.subplots(3, 2)
  fig.suptitle("Quadratic Position Control", size=20)

  for axes_ix, p in params.items():

    ax = axs[axes_ix[0], axes_ix[1]]
    x0 = p['x0']
    x1 = p['x1']
    v0 = p['v0']
    max_a = p['max_a']
    max_fwd_v = p['max_fwd_v']
    max_rev_v = p['max_rev_v']

    ax.set_title(p['title'])
    #ax.set_xlabel("Time")
    #ax.set_ylabel("Displacement")

    ax.set_xticks([0])
    ax.set_xticklabels(["$t = 0$"])
    ax.set_yticks([x0, x1])
    ax.set_yticklabels(["$x_0$", "$x_f$"])

    ax.axhline(x0, color='k', lw=0.5)
    ax.axhline(x1, color='b', lw=0.5)
    ax.axvline(0, color='k', lw=0.5)
    ax.plot([0, 0.46], [x0, x0 + 0.46 * v0], 'c', ls='-',
            label="Initial Rate of Change")
    ax.scatter([0], [x0], color='k', label="Initial State")

    # Rein in the current velocity if it is larger
    # larger than the maximum velocity.
    dv_rein = 0.0
    if v0 > max_fwd_v:
      dv_rein = max_fwd_v - v0
    elif v0 < -max_rev_v:
      dv_rein = -max_rev_v - v0
    a_rein = -sgn2(v0) * max_a
    dt_rein = abs(dv_rein) / max_a
    dx_rein = dt_rein * (v0 + 0.5 * dt_rein * a_rein)
    t_rein = 0.0
    x_rein = x0
    v_rein = v0
    t_turn = t_rein + dt_rein
    x_turn = x_rein + dx_rein
    v_turn = v_rein + dv_rein
    a_turn = -sgn2(v_turn) * max_a

    # Now that any overspeeding has been corrected, consider
    # (t_turn, x_turn, v_turn) to be the initial state.

    # Find the minimum stopping time and the displacement
    # at that time if full deceleration were applied.
    dt_msd = abs(v_turn) / max_a
    dx_msd = dt_msd * (v_turn + 0.5 * dt_msd * a_rein)
    t_at_msd = t_turn + dt_msd
    x_at_msd = x_turn + dx_msd

    t = linspace_step(t_turn, t_at_msd, plot_step)
    x = x_turn + (t - t_turn) * (v_turn + 0.5 * (t - t_turn) * a_turn)

    HeadingWrongWay = (x1 < x_turn) != (v_turn < 0)
    WillOvershoot = (x1 < x_at_msd) != (dx_msd < 0.0)

    if HeadingWrongWay or WillOvershoot:
      # Decelerate and reverse.
      ax.plot(t, x, 'r', label="Initial Deceleration")
      t_lurch = t_turn + dt_msd
      x_lurch = x_turn + dx_msd
      v_lurch = 0.0
      t_bplurch = t_lurch
      x_bplurch = x_lurch
      ax.scatter([t_lurch], [x_lurch], color='r', label="Reversal Point")
    else:
      # No turning is necessary. Proceed to lurch (or lurch even more).
      # (The full deceleration curve is plotted for comparison.)
      ax.plot(t, x, 'r', ls=':', label = "Maximum Deceleration Permitted")
      # Back-projected a past rest state.
      t_lurch = t_turn
      x_lurch = x_turn
      v_lurch = v_turn
      t_bplurch = t_lurch - dt_msd
      x_bplurch = x_lurch - dx_msd
      ax.scatter([t_bplurch], [x_bplurch], color='g', alpha=0.5,
                 label="Back-projected")

    # From here on, the position is a monotonic function.
    # It is convenient to pretend that it is constant
    # or monotonically increasing.
    dx = x1 - x_bplurch
    sgn_v = sgn2(dx)
    adx = abs(dx)
    max_v = max_rev_v if dx < 0.0 else max_fwd_v
    max_dx_for_triangular_v = (max_v * max_v) / max_a

    if adx <= max_dx_for_triangular_v:
      # Maximum speed not required
      dt_vramp = np.sqrt(adx / max_a)
      dx_for_triangular_v = adx
      lsd = 0.0
      lst = 0.0
      inflection_v = max_a * dt_vramp
    else:
      # Linear segment where maximum speed is sustained
      dt_vramp = max_v / max_a
      dx_for_triangular_v = max_dx_for_triangular_v
      lsd = adx - max_dx_for_triangular_v
      lst = lsd / max_v
      inflection_v = max_v

    # Acceleration
    a_lurch = sgn_v * max_a

    # Linear segment
    t_cruise = t_bplurch + dt_vramp
    x_cruise = x_bplurch + sgn_v * (0.5 * dx_for_triangular_v)
    v_cruise = v_brake = sgn_v * inflection_v
    a_cruise = 0.0

    # Deceleration
    t_brake = t_cruise + lst
    x_brake = x_cruise + sgn_v * lsd
    a_brake = -sgn_v * max_a

    # Rest
    t_rest = t_brake + dt_vramp
    x_rest = x_brake + sgn_v * (0.5 * dx_for_triangular_v)

    if dt_rein > 0:
      t = linspace_step(t_rein, t_rein + dt_rein, plot_step)
      x = x_rein + (t - t_rein) * (v_rein + 0.5 * (t - t_rein) * a_rein)
      ax.plot(t, x, '#cc0022', label="Initial Overspeed")
      ax.scatter([t_rein + dt_rein], [x_rein + dx_rein], color='r',
                 label="Overspeed corrected")
    if t_bplurch < t_turn:
      t = linspace_step(t_bplurch, t_turn, plot_step)
      x = x_bplurch + (0.5 * a_lurch * (t - t_bplurch)**2)
      ax.plot(t, x, 'g', ls='--', alpha=0.5, label="Back-projection")
    if dt_vramp > 0:
      t = linspace_step(max(t_turn, t_lurch), t_cruise, plot_step)
      x = x_lurch + (t - t_lurch) * (v_lurch + 0.5 * (t - t_lurch) * a_lurch)
      ax.plot(t, x, 'g', label="Acceleration")
    ax.vlines([t_at_msd], x_at_msd - 0.07, x_at_msd + 0.07, color='r')
    t = [t_cruise, t_brake]
    x = [x_cruise, x_brake]
    ax.scatter([t_cruise], [x_cruise], color='y',
               label="Start of Linear Segment")
    ax.plot(t, x, 'y', label="Linear segment")
    ax.scatter([t_brake], [x_brake], color='y',
               label="End of Linear Segment")
    t = linspace_step(t_brake, t_brake + dt_vramp, plot_step)
    x = x_brake + (t - t_brake) * (v_brake + 0.5 * (t - t_brake) * a_brake)
    ax.plot(t, x, '#DD00BB', label="Deceleration")
    ax.scatter([t_rest], [x_rest], color='b', label="Final State")

    if 0:
      t = []
      x = []
      v = []
      xi = []
      p1 = dict(p)
      Q = QPosCtrl()
      Q.target_x = p1['x1']
      Q.max_fwd_v = p1['max_fwd_v']
      Q.max_rev_v = p1['max_rev_v']
      Q.max_a = p1['max_a']
      Q.integral = 0.0
      t.append(0.0)
      x.append(Q.x)
      v.append(Q.v)
      xi.append(Q.integral)
      t_step = 0.01 + t_rest / 50.0
      for t_i in np.arange(0, t_rest * 1.1, t_step):
        Q.x = p1['x0']
        Q.v = p1['v0']
        Q.integral = 0.0
        Q.animate(t_i)
        t.append(t_i + t_step)
        x.append(Q.x)
        v.append(Q.v)
        xi.append(Q.integral)
      ax.axhline(0, color='orange', lw=0.5, ls=':')
      ax.plot(t, x, color='lime', lw=3, alpha=0.4)
      ax.plot(t, v, color='orange', lw=3, alpha=0.4)
      ax.plot(t, xi, color='m', lw=1, alpha=1.0)

    if 0:
      t = []
      x = []
      v = []
      xi = []
      p1 = dict(p)
      Q = QPosCtrl()
      Q.x = p1['x0']
      Q.target_x = p1['x1']
      Q.v = p1['v0']
      Q.max_fwd_v = p1['max_fwd_v']
      Q.max_rev_v = p1['max_rev_v']
      Q.max_a = p1['max_a']
      Q.integral = 0.0
      t.append(0.0)
      x.append(Q.x)
      v.append(Q.v)
      xi.append(Q.integral)
      t_step = 0.01 + t_rest / 50.0
      for t_i in np.arange(0, t_rest * 1.1, t_step):
        Q.animate(t_step)
        t.append(t_i + t_step)
        x.append(Q.x)
        v.append(Q.v)
        xi.append(Q.integral)
      ax.axhline(0, color='orange', lw=0.5, ls=':')
      ax.plot(t, x, color='lime', lw=3, alpha=0.4)
      ax.plot(t, v, color='orange', lw=3, alpha=0.4)
      ax.plot(t, xi, color='m', lw=3, alpha=1.0)

  plt.show()


if __name__ == '__main__':
  main()
