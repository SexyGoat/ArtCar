#!/usr/bin/env python3

import numpy as np
from matplotlib import pyplot as plt


STD_GRAVITY = 9.80665  # in metres per second per second


def eval_bezier(C, t):
  while len(C) > 1:
    A = C[:-1]
    B = C[1:]
    C = A + np.subtract(B, A) * t
  return C[0]


def bzt_turn_radius(left_speed, right_speed, axle_width):
  avg_speed = 0.5 * (right_speed + left_speed)
  diff_speed = (right_speed - left_speed)
  if abs(diff_speed) > 1e-12:
    radius = axle_width * avg_speed / diff_speed
  else:
    radius = float("inf")
  return radius


def main():

  def qr(a, b, c):
    det = b * b - 4 * a * c
    if det >= 0.0:
      r1 = 0.5 * (-b - np.sqrt(det)) / a
      r2 = 0.5 * (-b + np.sqrt(det)) / a
    else:
      r1 = None
      r2 = None
    return r1, r2

  max_speed = 6 + 0.0 * 27.777778  # metres per second
  max_lat_accel = 2.0 # (1.47m/s/s standard max. for highways)
  max_omega = np.radians(170)
  omega_reversing_slope = 1.0
  #max_omega = np.radians(162.05695) # Osculating P-H failure
  #max_braking_decel = 0.62 * STD_GRAVITY  # (0.47g to 0.62g for cars)

  v1 = qr(0.5 * max_lat_accel, -max_omega, max_lat_accel)[0]
  c = 1.0
  if v1 is not None:
    c = 0.5 * max_lat_accel / v1

  fig = plt.figure()
  ax = fig.subplots()

  v = np.linspace(-max_speed, max_speed, num=500)
  a = np.full_like(v, max_lat_accel)

  mla = max_lat_accel

  if 1:
    # Ad-hoc

    kappa = 1.2
    rho = 0.25
    rtss_multiplier = 4.0 * max_omega
    tss = np.exp(-((v/kappa)**2))
    r = 2.0 / (1.0 + np.exp(-(v/max_speed)/(kappa * rho))) - 1.0
    if 1:
      tss *= r * rtss_multiplier

    omega = tss

    a = omega * v

    ax.plot(v, omega, c='lime', ls='--', label="$\omega$ (Ad-hoc $\omega$)")
    ax.plot(v, a, c='brown', ls='--', label="$a$ (Ad-hoc $\omega$)")

  if 1:
    # Osculating parabola and hyperbola for omega (numerically unstable)

    omega = np.clip(mla / np.maximum(1e-9, np.abs(v)), -max_omega, max_omega)

    if v1 is not None:
      for i, v_i in enumerate(v):
        if -v1 < v_i < v1:
          omega[i] = max_omega - c * v_i ** 2

    # r = v / omega
    # a = omega**2 * r
    a = omega * v

    ax.plot(v, omega, c='y', ls='--',
        label="$\omega$ (Osculating trash $\omega$)")
    ax.plot(v, a, c='pink', ls='--',
        label="$a$ (Osculating trash $\omega$)")
    if v1 is not None:
      ax.axvline(v1, c='y', ls='--', lw=0.5)

  if 1:
    # Parabola and flatline for accel (kinked at v = 0)

    a[:] = mla
    c = 0.5 * max_omega ** 2 / mla
    v1 = max_omega / c
    for i, v_i in enumerate(v):
      if v_i < 0:
        a[i] = -a[i]
      if -v1 < v_i < v1:
        abs_v_i = abs(v_i)
        sgn_v_i = -1 if v_i < 0 else 1
        a[i] = sgn_v_i * (mla - 0.5 * c * ((abs_v_i - v1)) ** 2)
    omega = np.clip(a / v, 0, 4.5 * max_omega)

    ax.plot(v, omega, c='green', label="$\omega$ (Parabolic & flat $a$)")
    ax.plot(v, a, c='magenta', label="$a$ (Parabolic & flat $a$)")
    if v1 is not None:
      ax.axvline(v1, c='magenta', lw=0.5)

  if 1:
    # Sigmoid for accel (excellent for BZT steering and for cars)
    mla = mla
    a[:] = mla * (-1.0 + 2.0 / (1.0 + np.exp(-2 * max_omega / mla * v)))
    omega = np.clip(a / v, 0, 4.5 * max_omega)

    ax.plot(v, omega, c='#8800FF', label="$\omega$ (Sigmoid $a$)", lw=2)
    ax.plot(v, a, c='orange', label="$a$ (Sigmoid $a$)", lw=2)

  if 1:
    # Sigmoid for accel and omega (excellent for joystick cars)

    a[:] = mla * (-1.0 + 2.0 / (1.0 + np.exp(-2 * max_omega / mla * v)))
    omega = np.clip(a / v, 0, 4.5 * max_omega)
    s = (-1.0 + 2.0 / (1.0 + np.exp(-2 * omega_reversing_slope * v)))
    omega *= s
    a = omega * v

    ax.plot(v, omega, c='blue', label="$\omega$ (Sigmoid $a, \omega$)", lw=2)
    ax.plot(v, a, c='red', label="$a$ (Sigmoid $a, \omega$)", lw=2)

  ax.set_title("Hardest Turning Rates for Various Speeds", size=14)
  ax.set_xlabel("Speed (ms⁻¹)")
  ax.set_ylabel("Max Turn Rate, ω (rad/s), Max Lat. Accel, a (ms⁻²)")
  ax.set_xlim(-1.05 * max_speed, v[-1] * 1.02)
  ax.set_ylim(-max(max_omega, mla), max(max_omega, mla) * 1.05)
  ax.axhline(0, c='k', lw=0.5)
  ax.axvline(0, c='k', lw=0.5)
  ax.axhline(mla, c='red', lw=0.5)
  ax.axhline(max_omega, c='blue', lw=0.5)

  ax.legend(loc='lower right')
  fig.tight_layout()

  plt.show()


if __name__ == '__main__':
  main()
