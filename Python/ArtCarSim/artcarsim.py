#!/usr/bin/env python3

import os
import pygame as pg
import numpy as np
import numpy.linalg as la
import random
import serial
from enum import IntEnum
from enum import auto


if not pg.image.get_extended():
  raise SystemExit("Extended pygame image module required.")


class ViewMode (IntEnum):
  LOW_LOOK_N = 0
  HIGH_LOOK_N = 1
  ARSE = 2
  DRIVER = 3
  REMOTE = 4


class InputDeviceMode (IntEnum):
  MOUSE = 0
  JOYSTICK_ISO = 1
  JOYSTICKS_VH = 2  # Like a classic 2-channel RC remote
  JOYSTICKS_HPAT = 3  # Like the Arari Battlezone tank controls


class GamepadBtn (IntEnum):
  INVALID = 0
  A = 1
  B = 2
  X = 3
  Y = 4
  BACK = 5
  GUIDE = 6
  START = 7
  LEFTSTICK = 8
  RIGHTSTICK = 9
  LEFTSHOULDER = 10
  RIGHTSHOULDER = 11
  DPAD_UP = 12
  DPAD_DOWN = 13
  DPAD_LEFT = 14
  DPAD_RIGHT = 15
  TOUCHPAD = 16
  LEFTTRIGGER = 17
  RIGHTTRIGGER = 18


class GamepadAxis (IntEnum):
  INVALID = 0
  LEFTX = 1
  LEFTY = 2
  RIGHTX = 3
  RIGHTY = 4
  LEFTTRIGGER = 5
  RIGHTTRIGGER = 6


class GamepadMapping (object):

  bd = {
    'a': GamepadBtn.A,
    'b': GamepadBtn.B,
    'x': GamepadBtn.X,
    'y': GamepadBtn.Y,
    'back': GamepadBtn.BACK,
    'guide': GamepadBtn.GUIDE,
    'start': GamepadBtn.START,
    'leftstick': GamepadBtn.LEFTSTICK,
    'rightstick': GamepadBtn.RIGHTSTICK,
    'leftshoulder': GamepadBtn.LEFTSHOULDER,
    'rightshoulder': GamepadBtn.RIGHTSHOULDER,
    'lefttrigger': GamepadBtn.LEFTTRIGGER,
    'righttrigger': GamepadBtn.RIGHTTRIGGER,
    'dpup': GamepadBtn.DPAD_UP,
    'dpdown': GamepadBtn.DPAD_DOWN,
    'dpleft': GamepadBtn.DPAD_LEFT,
    'dpright': GamepadBtn.DPAD_RIGHT,
    'touchpad': GamepadBtn.TOUCHPAD,
  }

  ad = {
    'leftx': GamepadAxis.LEFTX,
    'lefty': GamepadAxis.LEFTY,
    'rightx': GamepadAxis.RIGHTX,
    'righty': GamepadAxis.RIGHTY,
    'lefttrigger': GamepadAxis.LEFTTRIGGER,
    'righttrigger': GamepadAxis.RIGHTTRIGGER,
  }

  def __init__(self, mapping_str):
    self.buttons = [-1] * len(GamepadBtn)
    self.axes = [-1] * len(GamepadAxis)
    self.hat_for_dpad = -1
    for item in mapping_str.split(","):
      if ":" in item:
        name, phys = item.split(":")
        if name in self.bd:
          x = self.bd[name]
          if x != 0:
            if phys[0] == 'b':
              self.buttons[x] = int(phys[1:])
            elif phys[0] == 'h':
              self.hat_for_dpad = int(phys[1])
        if name in self.ad:
          x = self.ad[name]
          if x != 0 and phys[0] == 'a':
            self.axes[x] = int(phys[1:])

  def btn(self, js, logical_btn_ix):
    result = False
    if js and logical_btn_ix >= 0:
      a = -1
      x = self.buttons[logical_btn_ix]
      if x >= 0:
        result = js.get_button(x)
      else:
        if logical_btn_ix == GamepadBtn.LEFTTRIGGER:
          a = self.axes[GamepadAxis.LEFTTRIGGER]
        elif logical_btn_ix == GamepadBtn.RIGHTTRIGGER:
          a = self.axes[GamepadAxis.RIGHTTRIGGER]
        else:
          if self.hat_for_dpad >= 0:
            if logical_btn_ix == GamepadBtn.DPAD_UP:
              result = js.get_hat(self.hat_for_dpad)[1] > 0
            elif logical_btn_ix == GamepadBtn.DPAD_DOWN:
              result = js.get_hat(self.hat_for_dpad)[1] < 0
            elif logical_btn_ix == GamepadBtn.DPAD_LEFT:
              result = js.get_hat(self.hat_for_dpad)[0] < 0
            elif logical_btn_ix == GamepadBtn.DPAD_RIGHT:
              result = js.get_hat(self.hat_for_dpad)[0] > 0
        if a >= 0:
          result = js.get_axis(a) >= -0.2
    return result

  def axis(self, js, logical_axis_ix):
    result = -1.0
    if js and logical_axis_ix >= 0:
      x = -1
      a = self.axes[logical_axis_ix]
      if a >= 0:
        result = js.get_axis(a)
      else:
        if logical_axis_ix == GamepadAxis.LEFTTRIGGER:
          x = self.buttons[GamepadBtn.LEFTTRIGGER]
        elif logical_axis_ix == GamepadAxis.RIGHTTRIGGER:
          x = self.buttons[GamepadBtn.RIGHTTRIGGER]
        if x >= 0:
          result = 1.0 if js.get_button(x) else -1.0
    return result


def find_known_gamepad(guid_str, known_gamepads):
  name = None
  mapping_str = None
  for i, item in enumerate(known_gamepads):
    name = item['names'].get(guid_str, None)
    if name is not None:
      mapping_str = item['mapping_str']
      break
  return (name, mapping_str)


known_gamepads = [
  {
    "names": {
      "030000008f0e00000610000000000000":
        "GreenAsia (Windows)",
    },
    "mapping_str": (
      "leftx:a0,lefty:a1,lefttrigger:b4,"
      "rightx:a5,righty:a2,righttrigger:b5,"
      "a:b2,b:b1,x:b3,y:b0,"
      "leftshoulder:b6,rightshoulder:b7,"
      "leftstick:b9,rightstick:b10,"
      "dpup:h0.1,dpdown:h0.4,dpleft:h0.8,dpright:h0.2,"
      "back:b8,start:b11"
    )
  },
  {
    "names": {
      "030000008f0e00000610000000010000":
        "GreenAsia Electronics Controller (Linux)",
    },
    "mapping_str": (
      "leftx:a0,lefty:a1,lefttrigger:b4,"
      "rightx:a3,righty:a2,righttrigger:b5,"
      "a:b2,b:b1,x:b3,y:b0,"
      "leftshoulder:b6,rightshoulder:b7,"
      "leftstick:b9,rightstick:b10,"
      "dpup:h0.1,dpdown:h0.4,dpleft:h0.8,dpright:h0.2,"
      "back:b8,start:b11"
    )
  },
  {
    "names": {
      "030000008f0e00000300000010010000":
        "PS3 Controller (Linux - GreenAsia Mode 1)",
    },
    "mapping_str": (
      "leftx:a0,lefty:a1,lefttrigger:b6,"
      "rightx:a2,righty:a3,righttrigger:b7,"
      "a:b2,b:b1,x:b3,y:b0,"
      "leftshoulder:b4,rightshoulder:b5,"
      "leftstick:b10,rightstick:b11,"
      "dpup:h0.1,dpdown:h0.4,dpleft:h0.8,dpright:h0.2,"
      "back:b8,start:b9"
    )
  },
  {
    "names": {
      "030000005e0400008e02000010010000":
        "Dead Xbox 360 Controller (Linux - GreenAsia Mode 2)",
    },
    "mapping_str": (
      "leftx:a0,lefty:a1,lefttrigger:a2,"
      "rightx:a3,righty:a4,righttrigger:a5,"
      "a:b0,b:b1,x:b2,y:b3,"
      "leftshoulder:b4,rightshoulder:b5,"
      "leftstick:b9,rightstick:b10,"
      "dpup:h0.1,dpdown:h0.4,dpleft:h0.8,dpright:h0.2,"
      "back:b6,guide:b8,start:b7"
    )
  },
  {
    "names": {
      "030000008f0e00001200000010010000":
        "GreenAsia USB Joystick (Linux)",
    },
    "mapping_str": (
      "leftx:a0,lefty:a1,lefttrigger:b5,"
      "rightx:a3,righty:a2,righttrigger:b7,"
      "a:b0,b:b1,x:b2,y:b3,"
      "leftshoulder:b4,rightshoulder:b5,"
      "leftstick:b10,rightstick:b11,"
      "dpup:h0.1,dpdown:h0.4,dpleft:h0.8,dpright:h0.2,"
      "back:b8,guide:b10,start:b9"
    )
  },
  {
    "names": {
      "030000008f0e00000300000007010000":
        "GreenAsia USB Joystick (Mac OS X)",
    },
    "mapping_str": (
      "leftx:a0,lefty:a1,lefttrigger:b5,"
      "rightx:a3,righty:a2,righttrigger:b7,"
      "a:b2,b:b3,x:b0,y:b1,"
      "leftshoulder:b4,rightshoulder:b6,"
      "dpup:h0.1,dpdown:h0.4,dpleft:h0.8,dpright:h0.2,"
      "back:b8,start:b9,touchpad:b13"
    )
  },
  {
    "names": {
      "050000004c0500006802000000800000":
        "PS3 Controller (Windows)",
    },
    "mapping_str": (
      "leftx:a0,lefty:a1,lefttrigger:a2,"
      "rightx:a3,righty:a4,righttrigger:a5,"
      "a:b0,b:b1,x:b3,y:b2,"
      "leftshoulder:b4,rightshoulder:b5,"
      "leftstick:b11,rightstick:b12,"
      "dpup:b13,dpdown:b14,dpleft:b15,dpright:b16,"
      "back:b8,guide:b10,start:b9,touchpad:b13"
    )
  },
  {
    "names": {
      "030000004c050000e60c000000000000":
        "PS5 Controller (Windows)",
    },
    "mapping_str": (
      "leftx:a0,lefty:a1,lefttrigger:a3,"
      "rightx:a2,righty:a5,righttrigger:a4,"
      "a:b1,b:b2,x:b3,y:b0,"
      "leftshoulder:b4,rightshoulder:b5,"
      "leftstick:b10,rightstick:b11,"
      "dpup:h0.1,dpdown:h0.4,dpleft:h0.8,dpright:h0.2,"
      "back:b8,guide:b12,start:b9,touchpad:b13"
    )
  },
  {
    "names": {
      "030000004c050000e60c000011010000":
        "PS5 Controller (Linux - Variant 1)",
      "050000004c050000e60c000000010000":
        "PS5 Controller (Linux - Variant 1)",
    },
    "mapping_str": (
      "leftx:a0,lefty:a1,lefttrigger:a3,"
      "rightx:a2,righty:a5,righttrigger:a4,"
      "a:b1,b:b2,x:b3,y:b0,"
      "leftshoulder:b4,rightshoulder:b5,"
      "leftstick:b10,rightstick:b11,"
      "dpup:h0.1,dpdown:h0.4,dpleft:h0.8,dpright:h0.2,"
      "back:b8,guide:b12,start:b9,touchpad:b13"
    )
  },
]

class TurnCaps (object):

  def __init__(self):
    self.max_lat_accel = 4.0  # (1.47m/s/s standard max. for highways)
    self.max_turn_rate = np.radians(90)
    self.reversing_omega_slope = 1.0  # For car-like stick-to-turn-centre mode
    self.reverse_turns = False  # Rev rate of change of heading for rev motion

  def max_turn_rate_for_speed(self, v):
    mla = self.max_lat_accel
    max_omega = self.max_turn_rate
    a = mla * (-1.0 + 2.0 / (1.0 + np.exp(-2.0 * max_omega / mla * v)))
    if abs(v) >= 1e-15:
      omega = max(0.0, min(max_omega, a / v))
    else:
      omega = max_omega
    if self.reverse_turns:
      # Reversing the vehicle preserves the direction of the turning
      # circle but reverses the sign of the rate of change of the heading.
      # (The joystick is pointed towards the turning centre.)
      s = (-1.0 + 2.0 / (1.0 + np.exp(-2.0 * self.reversing_omega_slope * v)))
      omega *= s
    else:
      # Reversing the vehicle preserves the sign of the rate of change
      # of the heading but flips the side on which the turning circle
      # appears. (RC toy tank, skid-steer. excavator, spacecraft, horse)
      pass
    return omega


class Blinkers (object):

  def __init__(self):
    self.input = 0  # Bit 1 = Left, bit 0 = Right
    self.prev_input = 0
    self.state = 0  # Bit 1 = Left, bit 0 = Right
    self.frequency = 1.2
    self.phase = 0.0

  def animate(self):
    oldstate = self.state
    presses = self.input & ~self.prev_input
    self.prev_input = self.input
    if presses:
      if self.state in (0, 3):
        self.state = self.input
      else:
        if self.input == 3:
          self.state = self.input
        else:
          if self.state == self.input:
            pass
          else:
            self.state = 0
    if self.state != oldstate:
      self.phase = 0.0

  def advance(self, delta_time):
    self.phase = (self.phase + delta_time * self.frequency) % 1.0


def joy_vv2xy(left, right):
  # left and right are each -1..0..+1 backward to forward.
  x = 0.5 * (left - right)
  y = 0.5 * (left + right)
  # x is -1..0..+1 left to right.
  # y is -1..0..+1 backward/down to forward/up.
  return (x, y)


def joy_xy2vv(x, y):
  # x is -1..0..+1 left to right.
  # y is -1..0..+1 backward/down to forward/up.
  left = max(-1.0, min(1.0, y + x))
  right = max(-1.0, min(1.0, y - x))
  # left and right are each -1..0..+1 backward to forward.
  return (left, right)


# Land vehicles have
# <x> = forward, <y> = left, <z> = up.
VIEW_SENSE_LAND_VEHICLE = np.array([
  [0.0, -1.0, 0.0],
  [0.0, 0.0, 1.0],
  [-1.0, 0.0, 0.0],
])

# Spaceships, Aircraft, ships, and submarines have
# <x> = forward, <y> = right, <z> = down
VIEW_SENSE_SPACE_VEHICLE = np.array([
  [0.0, 1.0, 0.0],
  [0.0, 0.0, -1.0],
  [-1.0, 0.0, 0.0],
])

# The OpenGL camera has
# <x> = right, <y> = up, <z> = backward
VIEW_SENSE_OPENGL = np.eye(3)


wfo_basis_vectors = (
  # Bounding point cloud or None
  None,
  # Vertices
  np.array([
    # Body outline
    (0.0, 0.0, 0.0),
    (1.0, 0.0, 0.0), (0.85, -0.07, 0.0), (0.85, 0.07, 0.0),
    (0.85, 0.0, -0.07), (0.85, 0.0, 0.07),
    (0.0, 1.0, 0.0), (0.07, 0.85, 0.0), (-0.07, 0.85, 0.0),
    (0.0, 0.85, 0.07), (0.0, 0.85, -0.07),
    (0.0, 0.0, 1.0), (-0.07, 0.0, 0.85), (0.07, 0.0, 0.85),
    (0.0, -0.07, 0.85), (0.0, 0.07, 0.85),
  ]),
  # Groups
  (
    # <x> (red)
    ((0xFF0000, None), ((0, 1, 2, 3, 1, 4, 5, 1),)),
    # <y> (green)
    ((0x00FF00, None), ((0, 6, 7, 8, 6, 9, 10, 6),)),
    # <z> (blue)
    ((0x0000FF, None), ((0, 11, 12, 13, 11, 14, 15, 11),)),
  ),
)


n = 10
k = 2.0 * np.pi / n

wfo_cylinder = (
  # Bounding point cloud or None
  None,
  # Vertices
  np.array(
    tuple((np.cos(k * i), np.sin(k * i), 0.0) for i in range(n)) +
    tuple((np.cos(k * i), np.sin(k * i), 1.0) for i in range(n))
  ),
  # Style groups
  (
    # Main Group
    (
      # Style
      (None, None),
      # Runs of connected lines
      (
        tuple((i % n) for i in range(n + 1)),
        tuple(n + (i % n) for i in range(n + 1)),
      ) + tuple(
        (i, n + i) for i in range(n)
      )
    ),
  ),
)


# Art car:
# body 2.9m wide, 6m long, drive wheels in middle.
# wheels 285mm wide 406.4mm dia. rims, 541.8mm tyre dia.

wfo_artcar1_ref_box = (
  # Bounding point cloud or None
  None,
  # Vertices
  np.array([
    (-3.0, 1.05, 0.0), (-3.0, -1.05, 0.0),
    (-2.8, 1.45, 0.0), (-2.8, -1.45, 0.0),
    (2.8, 1.45, 0.0), (2.8, -1.45, 0.0),
    (3.0, 1.05, 0.0), (3.0, -1.05, 0.0),
    (-3.0, 1.05, 0.3), (-3.0, -1.05, 0.3),
    (-2.8, 1.45, 0.3), (-2.8, -1.45, 0.3),
    (2.8, 1.45, 0.3), (2.8, -1.45, 0.3),
    (3.0, 1.05, 0.3), (3.0, -1.05, 0.3),
    (0.0, 1.25, 0.48), (0.0, -1.25, 0.48),
  ]),
  # Style groups
  (
    # Air cushion
    (
      (0x669900, 1),
      (
        (0, 2, 4, 6, 7, 5, 3, 1, 0),
        (8, 10, 12, 14, 15, 13, 11, 9, 8),
        (0, 8), (2, 10), (4, 12), (6, 14),
        (1, 9), (3, 11), (5, 13), (7, 15),
      )
    ),
    # Axle
    (
      (0xAA0088, 3),
      (
        (16, 17),
      )
    ),
  ),
)

wfo_artcar1_body = (
  # Bounding point cloud or None
  None,
  # Vertices
  np.array([
    # Slab outline
    (-3.0, 1.05, 0.0), (-3.0, -1.05, 0.0),
    (-2.8, 1.45, 0.0), (-2.8, -1.45, 0.0),
    (2.8, 1.45, 0.0), (2.8, -1.45, 0.0),
    (3.0, 1.05, 0.0), (3.0, -1.05, 0.0),
    (-3.0, 1.05, 0.9), (-3.0, -1.05, 0.9),
    (-2.8, 1.45, 0.9), (-2.8, -1.45, 0.9),
    (2.8, 1.45, 0.9), (2.8, -1.45, 0.9),
    (3.0, 1.05, 0.9), (3.0, -1.05, 0.9),
    # Wheel arches
    (-0.55, 1.45, 0.0), (-0.55, -1.45, 0.0),
    (-0.55, 1.45, 0.45), (-0.55, -1.45, 0.45),
    (-0.30, 1.45, 0.75), (-0.30, -1.45, 0.75),
    (0.30, 1.45, 0.75), (0.30, -1.45, 0.75),
    (0.55, 1.45, 0.45), (0.55, -1.45, 0.45),
    (0.55, 1.45, 0.0), (0.55, -1.45, 0.0),
    # Headlamps

  ]),
  # Style groups
  (
    # Base
    (
      (None, None),
      (
        (0, 2, 16, 18, 20, 22, 24, 26, 4, 6) +
        (7, 5, 27, 25, 23, 21, 19, 17, 3, 1, 0),
        (8, 10, 12, 14, 15, 13, 11, 9, 8),
        (0, 8), (2, 10), (4, 12), (6, 14),
        (1, 9), (3, 11), (5, 13), (7, 15),
      )
    ),
  ),
)

wfo_artcar1_headlamps = (
  # Bounding point cloud or None
  None,
  # Vertices
  np.array([
    # Left
    (2.81, 1.43, 0.42), (2.81, 1.43, 0.52),
    (2.91, 1.23, 0.52), (2.91, 1.23, 0.42),
    (2.81, 1.23, 0.42), (2.81, 1.23, 0.52),
    # Right
    (2.81, -1.43, 0.42), (2.81, -1.43, 0.52),
    (2.91, -1.23, 0.52), (2.91, -1.23, 0.42),
    (2.81, -1.23, 0.42), (2.81, -1.23, 0.52),
    # Inner pair
    (3.0, 0.7, 0.42), (3.0, 0.7, 0.52),
    (3.0, 0.9, 0.52), (3.0, 0.9, 0.42),
    (3.0, -0.7, 0.42), (3.0, -0.7, 0.52),
    (3.0, -0.9, 0.52), (3.0, -0.9, 0.42),
  ]),
  # Style groups
  (
    # Group
    (
      # Style determined by application
      (None, None),
      # Runs of connected lines
      (
        (0, 1, 2, 3, 0, 4, 5, 1), (4, 3), (5, 2),
        (6, 7, 8, 9, 6, 10, 11, 7), (10, 9), (11, 8),
        (12, 13, 14, 15, 12),
        (16, 17, 18, 19, 16),
      )
    ),
  ),
)

wfo_artcar1_left_di_lamps = (
  # Bounding point cloud or None
  None,
  # Vertices
  np.array([
    # Left rear
    (-2.81, 1.43, 0.3), (-2.81, 1.43, 0.4),
    (-2.86, 1.33, 0.4), (-2.86, 1.33, 0.3),
    # Left rear repeater
    (-2.1, 1.43, 0.36), (-2.1, 1.43, 0.40),
    (-2.3, 1.43, 0.40), (-2.3, 1.43, 0.36),
    # Left front repeater
    (2.1, 1.43, 0.36), (2.1, 1.43, 0.40),
    (2.3, 1.43, 0.40), (2.3, 1.43, 0.36),
    # Left front
    (2.81, 1.43, 0.3), (2.81, 1.43, 0.4),
    (2.86, 1.33, 0.4), (2.86, 1.33, 0.3),
  ]),
  # Style groups
  (
    # Group
    (
      # Style determined by application
      (None, None),
      # Runs of connected lines
      (
        (0, 1, 2, 3, 0),
        (4, 5, 6, 7, 4),
        (8, 9, 10, 11, 8),
        (12, 13, 14, 15, 12),
      )
    ),
  ),
)

wfo_artcar1_right_di_lamps = (
  # Bounding point cloud or None
  None,
  # Vertices
  wfo_artcar1_left_di_lamps[1] * np.array([1.0, -1.0, 1.0]),
  wfo_artcar1_left_di_lamps[2],
)

wfo_artcar1_stop_lamps = (
  # Bounding point cloud or None
  None,
  # Vertices
  np.array([
    # Left
    (-2.87, 1.31, 0.3), (-2.87, 1.31, 0.4),
    (-2.92, 1.21, 0.4), (-2.92, 1.21, 0.3),
    # Right
    (-2.87, -1.31, 0.3), (-2.87, -1.31, 0.4),
    (-2.92, -1.21, 0.4), (-2.92, -1.21, 0.3),
    # Centre
    (-3.0, 0.1, 0.75), (-3.0, 0.1, 0.80),
    (-3.0, -0.1, 0.80), (-3.0, -0.1, 0.75)
  ]),
  # Style groups
  (
    # Group
    (
      # Style determined by application
      (None, None),
      # Runs of connected lines
      (
        (0, 1, 2, 3, 0),
        (4, 5, 6, 7, 4),
        (8, 9, 10, 11, 8),
      )
    ),
  ),
)

wfo_artcar1_reversing_lamps = (
  # Bounding point cloud or None
  None,
  # Vertices
  np.array([
    # Left
    (-2.93, 1.19, 0.3), (-2.93, 1.19, 0.4),
    (-2.98, 1.09, 0.4), (-2.98, 1.09, 0.3),
    # Right
    (-2.93, -1.19, 0.3), (-2.93, -1.19, 0.4),
    (-2.98, -1.09, 0.4), (-2.98, -1.09, 0.3),
  ]),
  # Style groups
  (
    # Group
    (
      # Style determined by application
      (None, None),
      # Runs of connected lines
      (
        (0, 1, 2, 3, 0),
        (4, 5, 6, 7, 4),
      )
    ),
  ),
)

wfo_artcar_mcguffin = (
  # Bounding point cloud or None
  None,
  # Vertices
  np.array([
    # 0: Base and engine body
    (-0.98, 1.07, 0.0), (-0.98, -1.07, 0.0),
    (1.0, 1.07, 0.0), (1.0, -1.07, 0.0),
    (-1.11, 1.0, 0.4), (-1.11, -1.0, 0.4),
    (1.0, 1.2, 0.4), (1.0, -1.2, 0.4),
    (-1.11, 0.8, 0.0), (-1.11, -0.8, 0.0),
    (0.2, 1.07, 0.0), (0.2, -1.07, 0.0),
    (0.2, 1.3, 0.32), (0.2, -1.3, 0.32),
    (1.0, 1.2, 0.9),  (1.0, -1.2, 0.9),
    (1.0, 0.9, 1.4),  (1.0, -0.9, 1.4),
    (1.0, 0.3, 1.7),  (1.0, -0.3, 1.7),
    (0.2, 1.35, 0.9),  (0.2, -1.35, 0.9),
    (0.2, 0.96, 1.55),  (0.2, -0.96, 1.55),
    (0.2, 0.37, 1.85),  (0.2, -0.37, 1.85),
    (-1.11, 1.0, 0.85),  (-1.11, -1.0, 0.85),
    (-1.11, 0.75, 1.3),  (-1.11, -0.75, 1.3),
    (-1.11, 0.27, 1.57),  (-1.11, -0.27, 1.57),
    # 32: Exhaust cone
    (-2.3, 0.0, 0.7),
    (-0.71, 0.0, 1.2 * 0.4 + 0.7),
    (-0.71, 1.5 * 0.3804, 1.5 * 0.1236 + 0.7),
    (-0.71, 1.5 * -0.3804, 1.5 * 0.1236 + 0.7),
    (-0.71, 1.5 * 0.2351, 1.5 * -0.3236 + 0.7),
    (-0.71, 1.5 * -0.2351, 1.5 * -0.3236 + 0.7),
    # 38: Nose
    (2.1, 0.8, 0.0), (2.1, -0.8, 0.0),
    (2.25, 0.5, 0.5), (2.25, -0.5, 0.5),
    (3.46, 0.52, 0.0), (3.46, -0.52, 0.0),
    (3.46, 0.35, 0.32), (3.46, -0.35, 0.32),
    (3.46, 0.4, -0.35), (3.46, -0.4, -0.35),
    (3.46, 0.0, -0.52), (4.7, 0.0, -0.2),
    # 50: Windshield
    (2.1, 0.54, 0.8), (2.1, -0.54, 0.8),
    (2.613, 0.455, 0.446), (2.613, -0.455, 0.446),
  ]),
  # Style groups
  (
    # Base
    (
      (None, 2),
      (
        # Base and engine body
        (0, 2, 3, 1, 9, 8, 0),
        (8, 4), (9, 5), #(0, 4), (1, 5), (2, 6), (3, 7),
        (4, 12, 6), (5, 13, 7),
        (2, 6, 14, 16, 18, 19, 17, 15, 7, 3),
        (10, 12, 20, 22, 24, 25, 23, 21, 13, 11),
        (0, 4, 26, 28, 30, 31, 29, 27, 5, 1),
        (14, 20, 26), (16, 22, 28), (18, 24, 30),
        (19, 25, 31), (17, 23, 29), (15, 21, 27),
        (4, 10, 6), (5, 11, 7),
        # Exhaust cone
        (32, 33), (32, 34), (32, 35), (32, 36), (32, 37),
        (33, 34, 36, 37, 35, 33),
        # Nose
        (38, 39, 41, 40, 38),
        (42, 44, 45, 43, 47, 48, 46, 42),
        (38, 42, 49, 44, 40), (39, 43, 49, 45, 41),
        (46, 49, 47), (48, 49),
      )
    ),
    # windshield
    (
      (pg.Color(255, 255, 255), 2),
      (
        # Windshield
        (38, 52, 53, 39, 51, 50, 38), (50, 52), (51, 53)
      )
    ),
  ),
)

wfo_sc5k_ref_box = (
  # Bounding point cloud or None
  None,
  # Vertices
  np.array([
    (-1.0, 0.5, 0.0), (-1.0, -0.5, 0.0),
    (-0.05, 0.5, 0.0), (-0.05, -0.5, 0.0),
    (1.25, 0.5, 0.0), (1.25, -0.5, 0.0),
    (-1.0, 0.5, 0.2), (-1.0, -0.5, 0.2),
    (-0.05, 0.5, 0.2), (-0.05, -0.5, 0.2),
    (1.25, 0.5, 0.2), (1.25, -0.5, 0.2),
    (-0.05, 0.265, 0.25), (-0.05, -0.265, 0.25),
  ]),
  # Style groups
  (
    # Air cushion
    (
      (0x669900, 1),
      (
        (0, 2, 4, 5, 3, 1, 0),
        (6, 8, 10, 11, 9, 7, 6),
        (0, 6), (2, 8), (4, 10), (5, 11), (3, 9), (1, 7),
      )
    ),
    # Axle
    (
      (0xAA0088, 3),
      (
        (12, 13),
      )
    ),
  ),
)

wfo_sc5k_body = (
  # Bounding point cloud or None
  None,
  # Vertices
  np.array([
    # Body outline
    (-1.0, 0.5, 0.0), (-1.0, -0.5, 0.0),
    (0.0, 0.5, 0.0), (0.0, -0.5, 0.0),
    (1.25, 0.25, 0.0), (1.25, -0.25, 0.0),
    (-0.75, 0.2, 1.0), (-0.75, -0.2, 1.0),
    (0.0, 0.2, 1.0), (0.0, -0.2, 1.0),
    # Headlamp
    (0.9375, 0.180, 0.25), (0.9375, -0.180, 0.25),
    (1.0625, 0.180, 0.15), (1.0625, -0.180, 0.15),
  ]),
  # Style groups
  (
    # Main Group
    (
      # Style
      (None, None),
      # Runs of connected lines
      (
        (0, 2, 4, 5, 3, 1, 0),
        (6, 8, 9, 7, 6),
        (0, 6), (2, 8, 4), (1, 7), (3, 9, 5),
      )
    ),
    # Headlamp
    (
      # Style
      (0xFFFFFF, 1),
      # Runs of connected lines
      (
        (10, 11, 13, 12, 10),
      )
    ),
  ),
)

wfo_sc5k_left_di_lamps = (
  # Bounding point cloud or None
  None,
  # Vertices
  np.array([
    # Left rear
    (-0.95, 0.44, 0.2), (-0.925, 0.41, 0.3),
    (-0.925, 0.33, 0.3), (-0.95, 0.33, 0.2),
    # Left rear wrap-around to side
    (-0.85, 0.44, 0.2), (-0.85, 0.41, 0.3),
    # Left front
    (1.0, 0.24, 0.2), (0.9375, 0.2375, 0.25),
    (0.9375, 0.187, 0.25), (1.0, 0.187, 0.2),
    # Left front wrap-around to side
    (0.8, 0.28, 0.2), (0.8, 0.2628, 0.25),
  ]),
  # Style groups
  (
    # Group
    (
      # Style determined by application
      (0xFFAA00, None),
      # Runs of connected lines
      (
        (0, 1, 2, 3, 0, 4, 5, 1),
        (6, 7, 8, 9, 6, 10, 11, 7),
      )
    ),
  ),
)

wfo_sc5k_right_di_lamps = (
  # Bounding point cloud or None
  None,
  wfo_sc5k_left_di_lamps[1] * np.array([1.0, -1.0, 1.0]),
  wfo_sc5k_left_di_lamps[2],
)

wfo_sc5k_stop_lamps = (
  # Bounding point cloud or None
  None,
  # Vertices
  np.array([
    (-0.95, 0.32, 0.2), (-0.925, 0.32, 0.3),
    (-0.925, 0.23, 0.3), (-0.95, 0.23, 0.2),
    (-0.95, -0.32, 0.2), (-0.925, -0.32, 0.3),
    (-0.925, -0.23, 0.3), (-0.95, -0.23, 0.2),
    (-0.825, 0.08, 0.7), (-0.8, 0.08, 0.8),
    (-0.8, -0.08, 0.8), (-0.825, -0.08, 0.7),
  ]),
  # Style groups
  (
    # Group
    (
      # Style determined by application
      (None, None),
      # Runs of connected lines
      (
        (0, 1, 2, 3, 0), (4, 5, 6, 7, 4), (8, 9, 10, 11, 8),
      )
    ),
  ),
)

wfo_sc5k_reversing_lamps = (
  # Bounding point cloud or None
  None,
  # Vertices
  np.array([
    (-0.95, 0.22, 0.2), (-0.925, 0.22, 0.3),
    (-0.925, 0.13, 0.3), (-0.95, 0.13, 0.2),
    (-0.95, -0.22, 0.2), (-0.925, -0.22, 0.3),
    (-0.925, -0.13, 0.3), (-0.95, -0.13, 0.2),
  ]),
  # Style groups
  (
    # Group
    (
      # Style determined by application
      (None, None),
      # Runs of connected lines
      (
        (0, 1, 2, 3, 0), (4, 5, 6, 7, 4),
      )
    ),
  ),
)


def sloppy_joy(x, slop_hw=None):
  if slop_hw is None:
    slop_hw = 0.015
  g = 1.0 / (1.0 - slop_hw)
  if x > slop_hw:
    r = g * (x - slop_hw)
  elif x < -slop_hw:
    r = g * (x + slop_hw)
  else:
    r = 0.0
  return r


seven_seg_points = np.array([
  [0.0, 1.0], [1.0, 1.0], [1.0, 0.5], [1.0, 0.0], [0.0, 0.0], [0.0, 0.5],
  [1.30, 0.00],
  [1.25, 0.025], [1.35, 0.025], [1.35, -0.025], [1.25, -0.025],
])

seven_seg_runs = {
  "0": ((0, 1, 3, 4, 0),),
  "1": ((1, 3),),
  "2": ((0, 1, 2, 5, 4, 3),),
  "3": ((0, 1, 3, 4), (5, 2),),
  "4": ((0, 5, 2), (1, 3),),
  "5": ((1, 0, 5, 2, 3, 4),),
  "6": ((1, 0, 4, 3, 2, 5),),
  "7": ((0, 1, 3),),
  "8": ((5, 0, 1, 3, 4, 5, 2),),
  "9": ((2, 5, 0, 1, 3, 4),),
  "-": ((2, 5),),
  ".": ((7, 8, 9, 10, 7),),
}


def h4d_points(points):
  dw = 4 - points.shape[1]
  r = np.asanyarray(points)
  if dw > 0:
    a = np.zeros(dw).reshape((1, dw))
    a[0, -1] = 1.0
    r = np.hstack([points, np.tile(a, (points.shape[0], 1))])
  return r


def mtx4d_from_bvt(bvs, translation):
  M = np.pad(np.vstack([bvs, translation]), ((0, 0), (0, 1)))
  M[-1, -1] = 1.0
  return M


def look(direction, up, sense):
  backward = direction / -la.norm(direction)
  right = np.cross(up, backward)
  right /= la.norm(right)
  head_up = np.cross(backward, right)
  ori = sense.T @ np.vstack([right, head_up, backward])
  return ori


def mesh_to_segment_vertices(vertices, poly_edges):
  n = sum(len(pe) - 1 for pe in poly_edges if len(pe) >= 2)
  L = np.empty((2 * n, len(vertices[0])))
  i = 0
  for pe in poly_edges:
    if len(pe) >= 2:
      vix0 = pe[0]
      for vix1 in pe[1:]:
        L[i] = vertices[vix0]
        L[i + 1] = vertices[vix1]
        vix0 = vix1
        i += 2
  return L


class PoV (object):
  def __init__(self):
    self.pos = np.zeros([3])
    self.ori = np.eye(3)
    self.vel = np.zeros([3])


class ModelviewMtxStack (object):

  def __init__(self):
    self.matrix = np.eye(4)
    self.stack = list()

  def push(self):
    self.stack.append(self.matrix)
    self.matrix = np.array(self.stack[-1])

  def pop(self):
    if len(self.stack) > 0:
      self.matrix = self.stack.pop()
    else:
      self.matrix = np.eye(4)

  def translate(self, displ):
    d = np.pad(displ, (0, 3 - len(displ)))
    T = np.eye(4)
    T[3, :3] = d
    self.matrix = T @ self.matrix

  def scale(self, scale_factor, sy=None, sz=None):
    if sy is None and sz is None:
      sy = scale_factor
      sz = scale_factor
    else:
      if sy is None: sy = 1.0
      if sz is None: sz = 1.0
    T = np.diag((scale_factor, sy, sz, 1.0), 0)
    self.matrix = T @ self.matrix

  def rotate_x(self, angle_rad):
    c = np.cos(angle_rad)
    s = np.sin(angle_rad)
    R = np.eye(4)
    R[1:3, 1:3] = [
      [c, s],
      [-s, c],
    ]
    self.matrix = R @ self.matrix

  def rotate_y(self, angle_rad):
    c = np.cos(angle_rad)
    s = np.sin(angle_rad)
    R = np.eye(4)
    R[:3, :3] = [
      [c, 0.0, -s],
      [0.0, 1.0, 0.0],
      [s, 0.0, c],
    ]
    self.matrix = R @ self.matrix

  def rotate_z(self, angle_rad):
    c = np.cos(angle_rad)
    s = np.sin(angle_rad)
    R = np.eye(4)
    R[:2, :2] = [
      [c, s],
      [-s, c],
    ]
    self.matrix = R @ self.matrix

  def orient(self, ori):
    M = np.eye(4)
    M[:3, :3] = ori
    self.matrix = M @ self.matrix


class Perspective (object):

  def __init__(self, screen_size, hfov_deg, near=0.01, far=1e12):
    self.screen_size = screen_size
    self.hfov_deg = hfov_deg
    self.ori = np.eye(3)
    self.pos = np.zeros([3])
    self.sense = np.eye(3)
    self.near = near
    self.far = far
    self.update()

  def look_at(self, target, up):
    self.ori = look(target - self.pos, up, self.sense)

  def look(self, direction, up):
    self.ori = look(direction, up, self.sense)

  def update(self):
    s = 0.5 * max(self.screen_size)
    self.screen_mtx = np.array([[s, 0.0], [0.0, -s]])
    self.screen_centre = np.array([
      0.5 * self.screen_size[0],
      0.5 * self.screen_size[1],
    ])
    self.theta = np.radians(0.5 * self.hfov_deg)
    tan_theta = np.tan(self.theta)
    tan_phi = tan_theta * self.screen_size[1] / self.screen_size[0]
    self.phi = np.arctan(tan_phi)
    k = s / tan_theta
    self.screen_mtx2d = k * np.array([[1.0, 0.0], [0.0, -1.0]])
    T_trans = np.eye(4)
    T_trans[3, :3] = -self.pos
    T_orient = np.eye(4)
    T_orient[:3, :3] = self.ori.T
    T_sense = np.eye(4)
    T_sense[:3, :3] = self.sense.T
    self.matrix = T_trans @ T_orient @ T_sense

  def project_to_eye_space(self, points, model_view_mtx=None):
    if len(points) > 0:
      # Eye-space, homogeneous coordinates
      M = self.matrix
      if model_view_mtx is not None:
        M = model_view_mtx @ M
      points_hes = h4d_points(points) @ M
      # Divide by w.
      inv_w = ((1.0) / points_hes[:, 3]).reshape((len(points_hes), 1))
      # Eye-space, 3d coordinates (with +<z> behind camera)
      points_es = points_hes[:, :3] * inv_w
    else:
      points_es = np.array([])
    return points_es

  def project_es_to_screen(self, points_es):
    if len(points_es) > 0:
      # Divide by z.
      V = np.asanyarray(points_es)
      inv_z = (-1.0 / V[:, 2]).reshape(len(V), 1)
      # Eye-space, 2d coordinates
      points_es2d = V[:, :2] * inv_z
      # Display coordinates
      points_px = (points_es2d @ self.screen_mtx2d) + self.screen_centre
    else:
      points_px = np.array([])
    return points_px

  def project_noclip(self, points, model_view_mtx=None):
    if len(points) > 0:
      # Eye-space, homogeneous coordinates
      M = self.matrix
      if model_view_mtx is not None:
        M = model_view_mtx @ M
      points_hes = h4d_points(points) @ M
      # Divide by w, divide by z.
      inv_wz = (-1.0) / (points_hes[:, 2] * points_hes[:, 3])
      inv_wz = inv_wz.reshape((len(inv_wz), 1))
      # Eye-space, 2d coordinates
      points_es = points_hes[:, :2] * inv_wz
      # Display coordinates
      points_px = (points_es @ self.screen_mtx2d) + self.screen_centre
    else:
      points_px = np.array([])
    return points_px

  def clipped_edge_run_vertices(self, points_es, edge_runs):
    V = list()
    lsvs = mesh_to_segment_vertices(points_es, edge_runs)
    for i in range(0, len(lsvs), 2):
      A, B = lsvs[i : i + 2]
      a = A[2] + self.near
      b = B[2] + self.near
      if (a < 0) != (b < 0):
        A1 = A
        B1 = B
        t = a / (a - b)
        C = (A + (B - A) * t)
        C[2] = -self.near
        if a <= 0.0:
          B1 = C
        else:
          A1 = C
        V.append(A1)
        V.append(B1)
      else:
        if a <= 0:
          V.append(A)
          V.append(B)
    return V


def draw_wfo(surface, view, mvm, wfo, styles=None):
  bpc, vertices, groups = wfo
  group = groups[0]
  style, runs = group
  pe = view.project_to_eye_space(vertices, mvm.matrix)
  col = 0x0099ff
  lw = 1
  if styles is not None:
    if styles[0] is not None: col = styles[0]
    if styles[1] is not None: lw = styles[1]
  for style, runs in groups:
    gs = [None, None]
    gs[:min(len(style), len(gs))] = style
    gcol = col if gs[0] is None else gs[0]
    glw = lw if gs[1] is None else gs[1]
    C = view.clipped_edge_run_vertices(pe, runs)
    S = view.project_es_to_screen(C)
    for i in range(0, len(S), 2):
      pg.draw.line(surface, gcol, S[i], S[i + 1], width=glw)


def draw_ground_grid(surface, view, mvm, pos=None, grid_mode=None):
  if grid_mode is None: grid_mode = 3
  if grid_mode == 1:
    hw = 10
    spacing = 1.0
  elif grid_mode == 2:
    hw = 10
    spacing = 10.0
  elif grid_mode == 3:
    hw = 30
    spacing = 10.0
  elif grid_mode == 4:
    hw = 100
    spacing = 10.0
  elif grid_mode == 5:
    hw = 1000
    spacing = 1.0
  else:
    return
  n = 2 * hw + 1
  inv_spacing = 1.0 / spacing
  L = np.atleast_2d(np.linspace(-hw * spacing, hw * spacing, n)).T
  L1 = np.hstack([L, np.full((n, 1), -hw * spacing)])
  L2 = np.hstack([L, np.full((n, 1), +hw * spacing)])
  vertices = np.vstack([L1, L2])
  for axis in range(2):
    mvm.push()
    if pos is not None:
      qpos = np.array(pos[:2])
      qpos[0] = spacing * round(inv_spacing * qpos[0])
      qpos[1] = spacing * round(inv_spacing * qpos[1])
      mvm.translate(qpos)
    if axis == 1:
      mvm.orient([[0, 1, 0], [-1, 0, 0], [0, 0, 1]])
    pe = view.project_to_eye_space(vertices, mvm.matrix)
    runs = [(i, i + n) for i in range(n)]
    C = view.clipped_edge_run_vertices(pe, runs)
    S = view.project_es_to_screen(C)
    for i in range(0, len(S), 2):
      pg.draw.line(surface, 0x336699, S[i], S[i + 1])
    mvm.pop()


def draw_world_basis_vectors(surface, view, mvm):
  mvm.push()
  mvm.scale(1)
  draw_wfo(surface, view, mvm, wfo_basis_vectors, styles=(None, 3))
  mvm.pop()


def draw_flat_vector(surface, view, mvm, tail, tip, col, lw):
  tail2d = np.array(tail)[:2]
  tip2d = np.array(tip)[:2]
  displ = tip2d - tail2d
  length = la.norm(displ)
  if length > 1e-6:
    x = displ * 1.0 / length
    y = np.array([-x[1], x[0]])
    hl = min(0.4, 0.75 * length)
    tl = length - hl
    hhw = 0.4 * hl
    wfo_v = (
      None,
      np.array([
        (0, 0), (length, 0),
        (tl, +hhw), (tl, 0.0), (tl, -hhw),
      ]),
      (((col, lw), ((0, 3), (3, 2, 1, 4, 2),)),),
    )
    mvm.push()
    mvm.translate(tail2d)
    mvm.orient(np.array([
      [x[0], x[1], 0.0],
      [y[0], y[1], 0.0],
      [0.0, 0.0, 1.0],
    ]))
    draw_wfo(surface, view, mvm, wfo_v)
    mvm.pop()


def draw_robomouse_wheels(surface, view, mvm, auxstates=None):
  lwa = auxstates.get('lwa', 0.0)
  rwa = auxstates.get('rwa', 0.0)
  lws = abs(np.clip(auxstates.get('lw_twist', 0.0), -1.0, +1.0))
  rws = abs(np.clip(auxstates.get('rw_twist', 0.0), -1.0, +1.0))
  to = auxstates.get('traction_offset', np.array((0, 0, -0.2)))
  aw = auxstates.get('axle_width', 0.55)
  wr = auxstates.get('wheel_radius', 0.25)
  ww = auxstates.get('wheel_width', 0.25)
  std_col = np.array([204, 204, 204])
  stress_col = np.array([255, 0, 0])
  lw_col = std_col + lws * (stress_col - std_col)
  rw_col = std_col + rws * (stress_col - std_col)
  lw_styles = (pg.Color(lw_col), 1 + (lws > 0.9))
  rw_styles = (pg.Color(rw_col), 1 + (rws > 0.9))
  mvm.push()
  mvm.translate(to)
  wy = 0.5 * (aw - ww)
  mvm.push()
  mvm.translate((0.0, wy, wr))
  mvm.rotate_x(-0.5 * np.pi)
  mvm.scale(wr, wr, ww)
  mvm.rotate_z(lwa)
  draw_wfo(surface, view, mvm, wfo_cylinder, lw_styles)
  mvm.pop()
  mvm.push()
  mvm.translate((0.0, -wy, wr))
  mvm.rotate_x(0.5 * np.pi)
  mvm.scale(wr, wr, ww)
  mvm.rotate_z(-rwa)
  draw_wfo(surface, view, mvm, wfo_cylinder, rw_styles)
  mvm.pop()
  mvm.pop()


def draw_artcar1(surface, view, mvm, auxstates=None, styles=None):
  if auxstates is None: auxstates = {}
  stopping = auxstates.get('stop', False)
  reversing = auxstates.get('reversing', False)
  ldi = auxstates.get('ldi', False)
  rdi = auxstates.get('rdi', False)
  hl_styles = (0xFFFFFF, 1)
  sl_styles = ((0xAA0000, 1), (0xFF0000, 5))[stopping & 1]
  rl_styles = ((0xAAAAAA, 1), (0xFFFFFF, 5))[reversing & 1]
  di_styles = ((0x885500, 1), (0xFFAA00, 5))
  ldil_styles = di_styles[ldi & 1]
  rdil_styles = di_styles[rdi & 1]
  draw_robomouse_wheels(surface, view, mvm, auxstates)
  draw_wfo(surface, view, mvm, wfo_artcar1_body, styles)
  draw_wfo(surface, view, mvm, wfo_artcar1_headlamps, hl_styles)
  draw_wfo(surface, view, mvm, wfo_artcar1_stop_lamps, sl_styles)
  draw_wfo(surface, view, mvm, wfo_artcar1_left_di_lamps, ldil_styles)
  draw_wfo(surface, view, mvm, wfo_artcar1_right_di_lamps, rdil_styles)
  draw_wfo(surface, view, mvm, wfo_artcar1_reversing_lamps, rl_styles)
  mvm.push()
  mvm.translate((-1.5, 0.0, 0.9))
  mvm.scale(1.3)
  draw_wfo(surface, view, mvm, wfo_artcar_mcguffin, styles)
  mvm.pop()


def draw_sinclair_c5000(surface, view, mvm, auxstates=None, styles=None):
  if auxstates is None: auxstates = {}
  stopping = auxstates.get('stop', False)
  reversing = auxstates.get('reversing', False)
  ldi = auxstates.get('ldi', False)
  rdi = auxstates.get('rdi', False)
  sl_styles = ((0xAA0000, 1), (0xFF0000, 5))[stopping & 1]
  rl_styles = ((0xAAAAAA, 1), (0xFFFFFF, 5))[reversing & 1]
  di_styles = ((0x885500, 1), (0xFFAA00, 5))
  ldil_styles = di_styles[ldi & 1]
  rdil_styles = di_styles[rdi & 1]
  draw_robomouse_wheels(surface, view, mvm, auxstates)
  draw_wfo(surface, view, mvm, wfo_sc5k_body, styles)
  draw_wfo(surface, view, mvm, wfo_sc5k_stop_lamps, sl_styles)
  draw_wfo(surface, view, mvm, wfo_sc5k_reversing_lamps, rl_styles)
  draw_wfo(surface, view, mvm, wfo_sc5k_left_di_lamps, ldil_styles)
  draw_wfo(surface, view, mvm, wfo_sc5k_right_di_lamps, rdil_styles)


class QPosCtrl (object):

  def __init__(self):
    self.x = 0.0
    self.v = 0.0
    self.target_x = 0.0
    self.max_fwd_v = 1e6
    self.max_rev_v = 1e6
    self.max_a = 1e6
    self.integral = 0.0

  def advance(self, delta_time):

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


class MotorAccLimits (object):

  def __init__(self, accel, jerk):
    self.max_fwd_accel = accel
    self.max_fwd_decel = accel
    self.max_rev_accel = accel
    self.max_rev_decel = accel
    self.max_jerk = jerk

  def copy(self):
    x = MotorAccLimits(self.max_fwd_accel, self.max_jerk)
    x.max_fwd_decel = self.max_fwd_decel
    x.max_rev_accel = self.max_rev_accel
    x.max_rev_decel = self.max_rev_decel
    return x

  def load_blend(self, src0, src1, t):
    def blend(a, b, t):
      return a + t * (b - a)
    self.max_fwd_accel = blend(src0.max_fwd_accel, src1.max_fwd_accel, t)
    self.max_fwd_decel = blend(src0.max_fwd_decel, src1.max_fwd_decel, t)
    self.max_rev_accel = blend(src0.max_rev_accel, src1.max_rev_accel, t)
    self.max_rev_decel = blend(src0.max_rev_decel, src1.max_rev_decel, t)
    self.max_jerk = blend(src0.max_jerk, src1.max_jerk, t)

  @classmethod
  def full(cls, facc, fdec, racc, rdec, jerk):
    x = cls(facc, jerk)
    x.max_fwd_decel = fdec
    x.max_rev_accel = racc
    x.max_rev_decel = rdec
    return x


class SpeedCtrl (object):

  def __init__(self, motor_acc_limits):
    self.mal = motor_acc_limits
    self.v_pos_ctrl = QPosCtrl()
    self.max_speed = 0.1
    self.target_speed = 0.0
    self.current_speed = 0.0
    self.current_accel = 0.0

  def animate(self):

    if self.current_speed >= 0.0:
      max_acc = self.mal.max_fwd_accel
      max_dec = self.mal.max_fwd_decel
    else:
      max_acc = self.mal.max_rev_decel
      max_dec = self.mal.max_rev_accel

    # Using a position controller for velocity control means
    # that the controller's position (x), velocity (v) and
    # acceleration (a) correspond to velocity, acceleration
    # and jerk respectively.
    Q = self.v_pos_ctrl
    Q.max_fwd_v = max_acc
    Q.max_rev_v = max_dec
    Q.max_a = self.mal.max_jerk
    Q.x = self.current_speed
    Q.v = self.current_accel
    Q.target_x = self.target_speed

  def advance(self, delta_time):
    Q = self.v_pos_ctrl
    Q.advance(delta_time)
    self.current_accel = Q.v
    self.current_speed = Q.x


class CarSpeedCtrl (SpeedCtrl):

  def __init__(self, cruise_mal, braking_mal):
    mal = cruise_mal.copy()
    SpeedCtrl.__init__(self, mal)
    self.cruise_mal = cruise_mal
    self.braking_mal = braking_mal
    self.effective_mal = cruise_mal.copy()
    self.throttle_factor = 0.05
    self.enable_joy_brake = False
    self.joy_brake_speed_threshold = 0.2
    self.lever_pos = 0.0
    self.input_braking_factor = 0.0
    self.effective_braking_factor = 0.0
    self.joy_braking_state = 0

  def animate(self):

    ts0 = self.max_speed * self.lever_pos
    ts = self.current_speed + self.throttle_factor * (ts0 - self.current_speed)
    bf = 0.0
    dts = ts - self.current_speed

    if self.enable_joy_brake:
      if abs(self.current_speed) >= self.joy_brake_speed_threshold:
        if abs(ts0) >= self.joy_brake_speed_threshold:
          if (ts0 < 0.0) != (self.current_speed < 0.0):
            self.joy_braking_state = -1 if ts0 < 0 else +1
    else:
      self.joy_braking_state = 0
    if self.joy_braking_state == -1:
      if ts0 < -self.joy_brake_speed_threshold:
        bf = -self.lever_pos
        ts = ts0 = max(0.0, ts)
      else:
        self.joy_braking_state = 0
    elif self.joy_braking_state == +1:
      if ts0 > self.joy_brake_speed_threshold:
        bf = self.lever_pos
        ts = ts0 = min(0.0, ts)
      else:
        self.joy_braking_state = 0

    bf = max(bf, self.input_braking_factor)
    self.effective_braking_factor = bf

    self.mal.load_blend(self.cruise_mal, self.braking_mal, bf)
    ts *= (1.0 - bf)

    self.target_speed = ts
    SpeedCtrl.animate(self)


class WheelState (object):

  def __init__(self, radius, width):
    self.radius = radius
    self.width = width
    self.angle = 0.0
    self.linspeed = 0.0
    self.ls_integral = 0.0
    self.twist = 0.0   # Scrubbing from -1..0..+1


class RoboMouse (object):

  def __init__(self):
    self.pos = np.zeros(3)
    self.ori = np.eye(3)
    self.traction_offset = np.array([-0.05, 0.0, -0.2])
    self.driver_offset = np.array([0.05, 0.0, 0.8])
    self.axle_width = 0.55
    wheel_radius = 0.25
    wheel_width = 0.2
    self.lw_state = WheelState(wheel_radius, wheel_width)
    self.rw_state = WheelState(wheel_radius, wheel_width)
    self.blinkers = Blinkers()
    self.instr_turn_centre = None
    self.instr_lat_accel = np.zeros(3)
    self.instr_accel = np.zeros(3)
    self.instr_omega = 0.0
    self.instr_last_vel = np.zeros(3)
    self.stop_lamp_lit = False
    self.draw_fn = draw_sinclair_c5000
    self.draw_fn_styles = None

  def plonk(self, pos, heading):
    if heading is not None:
      c = np.cos(heading)
      s = np.sin(heading)
      self.ori = np.array([
        [c, s, 0.0],
        [-s, c, 0.0],
        [0.0, 0.0, 1.0],
      ])
    if pos is not None:
      self.pos[:2] = pos[:2]
      self.pos[2] = -self.traction_offset[2]

  def animate(self):
    pass

  def advance(self, delta_time):
    self.instr_turn_centre = None
    for ws in (self.lw_state, self.rw_state):
      ws.angle += delta_time * ws.linspeed / ws.radius
      ws.angle %= (2.0 * np.pi)
    #ld = self.lw_state.linspeed * delta_time
    #rd = self.rw_state.linspeed * delta_time
    ld = self.lw_state.ls_integral
    rd = self.rw_state.ls_integral
    a = 0.5 * (rd + ld)
    b = (rd - ld)
    r = None
    if abs(b) > 1e-6:
      r = self.axle_width * a / b
      if abs(r) > 1e-6:
        # Normal turn
        beta = a / r
        dx = r * np.sin(beta)
        dy = r * (np.cos(beta) - 1.0)
      else:
        # Turning on the spot
        r = 0.0
        dx = 0.0
        dy = 0.0
        beta = b / self.axle_width
    else:
      # Very straight
      beta = b / self.axle_width
      dx = a
      dy = 0.0
    tc = self.pos + self.traction_offset @ self.ori
    tc += dx * self.ori[0] + dy * self.ori[1]
    hdg = np.arctan2(self.ori[0][1], self.ori[0][0])
    hdg += beta
    self.ori[0] = [np.cos(hdg), np.sin(hdg), 0.0]
    self.ori[2] = [0.0, 0.0, 1.0]
    self.ori[0] / la.norm(self.ori[0])
    self.ori[1] = np.cross(self.ori[2], self.ori[0])
    self.pos = tc - self.traction_offset @ self.ori
    self.instr_lat_accel = np.zeros(3)
    self.instr_omega = 0.0
    if r is not None:
      r_vect = [0.0, r, 0.0] @ self.ori
      self.instr_turn_centre = tc + r_vect
      diff_speed = self.rw_state.linspeed - self.lw_state.linspeed
      self.instr_omega = diff_speed / self.axle_width
      self.instr_lat_accel = (self.instr_omega ** 2) * r_vect

  def draw(self, screen, view, mvm, aux_overrides=None):
    mvm.push()
    mvm.translate(self.pos)
    mvm.orient(self.ori)
    speed = 0.5 * (self.rw_state.linspeed + self.lw_state.linspeed)
    aux = dict()
    aux['lwa'] = self.lw_state.angle
    aux['rwa'] = self.rw_state.angle
    aux['lw_twist'] = self.lw_state.twist
    aux['rw_twist'] = self.rw_state.twist
    aux['stop'] = self.stop_lamp_lit
    aux['reversing'] = speed < -0.001
    ph = 1 if self.blinkers.phase < 0.5 else 0
    aux['ldi'] = (((self.blinkers.state >> 1) & 1) and ph)
    aux['rdi'] = (((self.blinkers.state >> 0) & 1) and ph)
    aux['traction_offset'] = self.traction_offset
    aux['axle_width'] = self.axle_width
    aux['wheel_radius'] = self.lw_state.radius
    aux['wheel_width'] = self.lw_state.width
    if aux_overrides is not None:
      aux.update(aux_overrides)
    self.draw_fn(screen, view, mvm, aux, self.draw_fn_styles)
    mvm.pop()


def draw_digit_7seg(surface, stdrect, col, ch, skew=None, segwidth=1):
  if skew is None: skew = 0.17632698  # tan(10 degrees)
  M = np.array([
    [stdrect.w, 0.0],
    [skew * stdrect.h, -stdrect.h],
  ])
  P = (seven_seg_points @ M) + np.array(stdrect.bottomleft)
  for run in seven_seg_runs.get(ch, ()):
    pg.draw.lines(
      surface,
      col,
      closed=False,
      points=[P[i] for i in run],
      width=segwidth,
    )


def draw_nstr_7seg(
  surface,
  leading_rect,
  col, nstr,
  skew=None,
  seg_lw=1,
  small_decimals=False,
):
  if skew is None: skew = 0.17632698  # tan(10 degrees)
  R = leading_rect.copy()
  for ch in nstr:
    if ch == '.':
      if small_decimals:
        s = 0.6
        R = pg.Rect((R.left, R.top), (s * R.w, s * R.h))
      R.right = R.left - 0.6 * R.width
      draw_digit_7seg(surface, R, col, ch, skew, seg_lw)
      R.left = R.right + 0.6 * R.width
    else:
      draw_digit_7seg(surface, R, col, ch, skew, seg_lw)
      R.left = R.right + 0.6 * R.width


def draw_knob(surface, pos, radius, knob_col=None):

  if knob_col is None:
    knob_col = pg.Color(255, 0, 0, 255)
  knob_shade_col = pg.Color(knob_col)
  knob_shade_col.a = int(round(0.6 * knob_shade_col.a))
  knob_shade_col = knob_shade_col.premul_alpha()
  knob_shade_col.a = 255
  r1 = 0.85 * radius
  r2 = 0.3 * r1
  dpos = pos + 0.9 * np.array([r1 - radius, r1 - radius])
  spos = dpos + 0.3 * np.array([r2 - r1, r2 - r1])
  pg.draw.circle(surface, knob_shade_col, pos, radius)
  pg.draw.circle(surface, knob_col, dpos, r1)
  pg.draw.circle(surface, (255, 255, 255, 255), spos, r2)


def draw_joystick(surface, joystick, margin=None, knob_col=None, mouse=False):

  shape = np.array([surface.get_width(), surface.get_height()])
  rect = pg.Rect((0, 0), shape)
  im = margin if margin else int(round(0.1 * max(shape)))
  fsd_rect = rect.inflate(-2 * im, -2 * im)
  hsd_rect = fsd_rect.inflate(
    -0.5 * fsd_rect.width, -0.5 * fsd_rect.height
  )
  centre = np.rint(0.5 * shape)
  gcol1 = (0, 100, 160, 255)
  gcol2 = (0, 50, 120, 255)
  X = [
    fsd_rect.left,
    hsd_rect.left,
    centre[0],
    hsd_rect.right,
    fsd_rect.right,
  ]
  Y = [
    fsd_rect.top,
    hsd_rect.top,
    centre[1],
    hsd_rect.bottom,
    fsd_rect.bottom,
  ]
  lines = (
    ((X[1], Y[0]), (X[1], Y[4]), gcol2),
    ((X[3], Y[0]), (X[3], Y[4]), gcol2),
    ((X[0], Y[1]), (X[4], Y[1]), gcol2),
    ((X[0], Y[3]), (X[4], Y[3]), gcol2),
    ((X[2], Y[0]), (X[2], Y[4]), gcol1),
    ((X[0], Y[2]), (X[4], Y[2]), gcol1),
  )
  for A, B, col in lines:
    pg.draw.line(surface, col, A, B, width=1)
  if not mouse:
    pg.draw.ellipse(surface, gcol1, fsd_rect, width=1)
  pg.draw.rect(surface, gcol1, fsd_rect, width=1)
  # Knob position
  displ = np.rint(np.multiply(joystick, [hsd_rect.w, -hsd_rect.h]))
  knob = centre + displ
  if mouse:
    hw = np.rint(0.65 * im)
    pg.draw.line(surface, knob_col, knob + [-hw, 0], knob + [hw, 0], width=3)
    pg.draw.line(surface, knob_col, knob + [0, -hw], knob + [0, hw], width=3)
  else:
    # Boot
    rb = np.rint(0.9 * im)
    bs = centre + im * np.array([-0.3, -0.3])
    pg.draw.circle(surface, (0, 0, 0, 255), centre, rb)
    pg.draw.circle(surface, (96, 96, 96, 255), centre, rb, width=1)
    pg.draw.circle(surface, (96, 96, 96, 255), bs, 0.3 * rb)
    # Shaft
    s = 0.55 * im / max(hsd_rect.w, -hsd_rect.h)
    shaft_base = centre + s * displ
    pg.draw.line(surface, (96, 96, 96, 255), shaft_base, knob, width=4)
    # Knob
    radius = np.rint(0.75 * im)
    draw_knob(surface, knob, radius, knob_col)


def draw_lever(
  surface,
  deflection,
  signed=True,
  margin=None,
  knob_col=None,
  horizontal=False,
):

  if horizontal:
    M = np.array([[0.0, 1.0], [1.0, 0.0]])
  else:
    M = np.array([[1.0, 0.0], [0.0, 1.0]])

  shape = np.array([surface.get_width(), surface.get_height()]) @ M
  im = margin if margin else int(round(0.1 * max(shape)))
  centre = np.rint(0.5 * shape)
  gcol1 = (0, 100, 160, 255)
  gcol2 = (0, 50, 120, 255)
  X = [
    im,
    centre[0],
    shape[0] - im,
  ]
  Y = [
    im,
    0.5 * (centre[1] + im),
    centre[1],
    0.5 * (centre[1] + shape[1] - im),
    shape[1] - im,
  ]
  lines = (
    ((X[0], Y[1]), (X[2], Y[1]), gcol2),
    ((X[0], Y[3]), (X[2], Y[3]), gcol2),
    ((X[0], Y[0]), (X[2], Y[0]), gcol1),
    ((X[0], Y[2]), (X[2], Y[2]), gcol1),
    ((X[0], Y[4]), (X[2], Y[4]), gcol1),
    ((X[1], Y[0]), (X[1], Y[4]), gcol1),
  )
  for A, B, col in lines:
    pg.draw.line(surface, col, A @ M, B @ M, width=1)
  # Knob position
  zero_ix = 2 if signed else 4
  displ_centre = np.array([X[1], Y[zero_ix]]) @ M
  displ = np.array([0.0, int(round(deflection * (Y[0] - Y[zero_ix])))]) @ M
  if horizontal:
    displ[0] = -displ[0]
  knob = displ_centre + displ
  # Boot
  rb = np.rint(0.9 * im)
  bs = displ_centre + im * np.array([-0.3, -0.3])
  pg.draw.circle(surface, (0, 0, 0, 255), displ_centre, rb)
  pg.draw.circle(surface, (96, 96, 96, 255), displ_centre, rb, width=1)
  pg.draw.circle(surface, (96, 96, 96, 255), bs, 0.3 * rb)
  # Shaft
  s = 0.55 * im / (Y[4] - Y[0])
  shaft_base = displ_centre + s * displ
  pg.draw.line(surface, (96, 96, 96, 255), shaft_base, knob, width=4)
  # Knob
  radius = np.rint(0.75 * im)
  draw_knob(surface, knob, radius, knob_col)


def draw_gauge(
  surface,
  dest_rect,
  mtr_deflection,
  cmd_deflection,
  target,
  mtr_defl_col=None,
  cmd_defl_col=None,
  target_col=None,
  signed=True,
  mirrored=False,
  horizontal=False,
):
  gcol1 = pg.Color(0, 100, 160)
  gcol2 = pg.Color(0, 50, 120)
  mcol = pg.Color(255, 255, 255) if mtr_defl_col is None else mtr_defl_col
  ccol = pg.Color(255, 255, 255) if cmd_defl_col is None else cmd_defl_col
  tcol = pg.Color(64, 255, 0) if target_col is None else target_col
  if horizontal:
    M = np.array([[0.0, 1.0], [1.0, 0.0]])
    tdr = pg.Rect(
      (dest_rect.top, dest_rect.left),
      (dest_rect.height, dest_rect.width),
    )
    rev = True
  else:
    M = np.array([[1.0, 0.0], [0.0, 1.0]])
    tdr = dest_rect
    rev = False
  shape = np.array([dest_rect.w, dest_rect.h]) @ M
  X = [
    tdr.left - 0.15 * tdr.w,
    tdr.left,
    tdr.centerx,
    tdr.right,
    tdr.right + 0.85 * tdr.w,
  ]
  if mirrored:
    X = [tdr.left + tdr.right - x for x in X]
  Y = [
    tdr.top,
    0.5 * (tdr.top + tdr.centery),
    tdr.centery,
    0.5 * (tdr.bottom + tdr.centery),
    tdr.bottom,
  ]
  lines = (
    (((X[2], Y[1]), (X[3], Y[1])), gcol2),
    (((X[2], Y[3]), (X[3], Y[3])), gcol2),
    (((X[1], Y[2]), (X[3], Y[2])), gcol1),
    (((X[1], Y[0]), (X[3], Y[0]), (X[3], Y[4]), (X[1], Y[4])), gcol1),
  )
  for run, col in lines:
    points = run @ M
    pg.draw.lines(surface, col, False, points, width=1)
  if mtr_deflection is not None:
    d = 0.5 + 0.5 * mtr_deflection if signed else mtr_deflection
    y = tdr.top + tdr.h * d if rev else tdr.bottom - tdr.h * d
    dy = 0.5 * tdr.w
    points = ((X[0], y - dy), (X[3], y), (X[0], y + dy)) @ M
    pg.draw.lines(surface, mcol, True, points)
  if cmd_deflection is not None:
    d = 0.5 + 0.5 * cmd_deflection if signed else cmd_deflection
    y = tdr.top + tdr.h * d if rev else tdr.bottom - tdr.h * d
    f = 1.0 if mtr_deflection is None else 0.6667
    dy = f * 0.5 * tdr.w
    x = X[3] + f * (X[0] - X[3])
    points = ((x, y - dy), (X[3], y), (x, y + dy)) @ M
    pg.draw.polygon(surface, ccol, points)
  if target is not None:
    d = 0.5 + 0.5 * target if signed else target
    y = tdr.top + tdr.h * d if rev else tdr.bottom - tdr.h * d
    points = ((X[3], y), (X[4], y)) @ M
    pg.draw.line(surface, tcol, points[0], points[1], width=3)


def draw_lr_gauges(
  surface,
  mtr_deflections,
  cmd_deflections,
  targets,
  mtr_defl_cols,
  cmd_defl_cols,
  target_cols,
  signed=None,
  margin=None,
):
  shape = surface.get_width(), surface.get_height()
  im = margin if margin else int(round(0.1 * max(shape)))
  gw = (shape[0] - 2 * im) * 0.25
  gutter = 2.0 * im
  lgrect = pg.Rect((im, im), (gw, shape[1] - 2 * im))
  rgrect = lgrect.copy()
  rgrect.right = shape[0] - im
  draw_gauge(
    surface,
    lgrect,
    mtr_deflections[0],
    cmd_deflections[0],
    targets[0],
    mtr_defl_cols[0],
    cmd_defl_cols[0],
    target_cols[0],
    True,
    False,
  )
  draw_gauge(
    surface,
    rgrect,
    mtr_deflections[1],
    cmd_deflections[1],
    targets[1],
    mtr_defl_cols[1],
    cmd_defl_cols[1],
    target_cols[1],
    True,
    True,
  )


def draw_steering_wheel_icon(surface, dest_rect, col=None):
  if col is None: col = pg.Colour(255, 255, 255)
  u = max(1, int(round(min(dest_rect.w, dest_rect.h) / 15)))
  pg.draw.ellipse(surface, col, dest_rect, u)
  hw = 0.5 * (dest_rect.right - dest_rect.left)
  hh = 0.5 * (dest_rect.bottom - dest_rect.top)
  uv = u * dest_rect.h / dest_rect.w
  cx = dest_rect.left + hw
  cy = dest_rect.top + hh
  y = cy + 0.5 * (hh - uv)
  dx = (hw - 0.5 * uv) * 0.5 * np.sqrt(3)
  p = cy - (hw - 0.5 * u)
  pg.draw.line(surface, col, (cx, cy), (cx, p), u)
  pg.draw.line(surface, col, (cx, cy), (cx - dx, y), u)
  pg.draw.line(surface, col, (cx, cy), (cx + dx, y), u)
  R = dest_rect.inflate(int(round(-1.4 * hw)), int(round(-1.4 * hh)))
  pg.draw.ellipse(surface, col, R, 0)


def draw_im_icon(surface, dest_rect, input_mod_ix, col=None):
  if col is None: col = pg.Colour(255, 255, 255)
  u = max(1, int(round(min(dest_rect.w, dest_rect.h) / 20)))
  cx, cy = dest_rect.center
  hw = 0.35 * dest_rect.w
  hh = 0.35 * dest_rect.h
  s = -(u & ~1) if u & 1 else -(u - 1)
  brect = dest_rect.inflate(s, s)
  pg.draw.rect(surface, col, brect, u)
  if input_mod_ix == 0:
    y = cy - 0.5 * hh
    pg.draw.line(surface, col, (cx - hw, y), (cx + hw, y), width=u)
    y = cy + 0.5 * hh
  if input_mod_ix in (1, 2):
    mla = 1.0
    mo = 1.2
    points = []
    for i in range(-30, 31):
      x = cx + hw * i / 30.0
      v = i * (0.2 if input_mod_ix == 2 else 0.08)
      a = mla * (-1.0 + 2.0 / (1.0 + np.exp(-2.0 * mo / mla * v)))
      y = max(0.0, min(mo, a / v)) if abs(v) >= 1e-15 else mo
      if input_mod_ix == 2:
        ros = 0.8
        y = y * (-1.0 + 2.0 / (1.0 + np.exp(-2.0 * ros * v)))
      else:
        y = y - 0.5
      y = cy - hh * y
      points.append((x, y))
    pg.draw.lines(surface, col, False, points, width=u)
    y = cy + hh * (0.5 if input_mod_ix == 1 else 0)
  if input_mod_ix in (0, 1):
    n = 3
    dm = 2
    ds = 4
    un = n * (dm + ds) - ds
    us = (2 * hw) / un
    x0 = cx - hw
    for i in range(0, n):
      x1 = x0 + us * (dm + ds) * i
      x2 = x1 + us * dm
      pg.draw.line(surface, col, (x1, y), (x2, y), width=u)


def draw_motor_icon(surface, dest_rect, col=None, magic=False):
  if col is None: col = pg.Colour(255, 255, 255)
  u = max(1, int(round(min(dest_rect.w, dest_rect.h) / 25)))
  hw = 0.5 * (dest_rect.right - dest_rect.left)
  hh = 0.5 * (dest_rect.bottom - dest_rect.top)
  cx = dest_rect.left + hw
  cy = dest_rect.top + hh
  d = min(dest_rect.w * 3 // 4, dest_rect.h)
  C = dest_rect.inflate(d - dest_rect.w, d - dest_rect.h)
  B = dest_rect.inflate(-2 * u, 2 * C.h // 4 - dest_rect.h)
  pg.draw.ellipse(surface, col, C, u)
  s = ((B.w - int(round(np.sqrt(d * d - B.h * B.h)))) + u) // 2
  points_l = np.array([
    (B.left + s, B.top), B.topleft, B.bottomleft, (B.left + s, B.bottom)
  ]) + np.array([-2, 0])
  points_r = np.array([
    (B.right - s, B.top), B.topright, B.bottomright, (B.right - s, B.bottom)
  ])
  k = np.radians(144)
  points_p = np.array([(np.sin(k * i), -np.cos(k * i)) for i in range(6)])
  points_p = 0.5 * (d - u) * points_p + (cx, cy)
  pg.draw.lines(surface, col, False, points_l, u)
  pg.draw.lines(surface, col, False, points_r, u)
  pg.draw.lines(surface, col, False, points_p, u)


def draw_joy_brake_icon(surface, dest_rect, col=None):
  if col is None: col = pg.Colour(255, 255, 255)
  u = max(1, int(round(min(dest_rect.w, dest_rect.h) / 20)))
  hw = 0.5 * (dest_rect.right - dest_rect.left)
  hh = 0.5 * (dest_rect.bottom - dest_rect.top)
  pg.draw.arc(surface, col, dest_rect, -0.25 * np.pi, 0.25 * np.pi, u)
  pg.draw.arc(surface, col, dest_rect, 0.75 * np.pi, 1.25 * np.pi, u)
  a = dest_rect.w * 1 // 4
  R = dest_rect.inflate(-a, -a)
  q = a / R.h
  pg.draw.arc(surface, col, R, 0.5 * np.pi + q, 0.5 * np.pi - q, u)
  R = pg.Rect((0, 0), (a + u, a + u))
  R.midtop = dest_rect.midtop
  pg.draw.ellipse(surface, col, R, u)
  b = max(1, int(round(0.75 * a)))
  R = pg.Rect((0, 0), (b, b))
  R.center = dest_rect.center
  pg.draw.ellipse(surface, col, R, 0)
  pg.draw.line(
    surface,
    col,
    dest_rect.center,
    (dest_rect.centerx, a + 0.5 * u),
    u,
  )


def draw_throttle_icon(surface, dest_rect, col=None):
  if col is None: col = pg.Colour(255, 255, 255)
  u = max(1, int(round(min(dest_rect.w, dest_rect.h) / 20)))
  s = max(1, 5 * dest_rect.w // 12)
  r = 9 * dest_rect.w // 12
  L = pg.Rect((s - 2 * r, -(2 * r - dest_rect.h) // 2), (2 * r, 2 * r))
  R = pg.Rect((dest_rect.w - s, -(2 * r - dest_rect.h) // 2), (2 * r, 2 * r))
  a = np.arcsin(min(0.99, (0.5 * dest_rect.h - 0.1 * u) / r))
  pg.draw.arc(surface, col, L, -a, a, u)
  pg.draw.arc(surface, col, R, np.pi - a, np.pi + a, u)
  r = 0.55 * min(dest_rect.w, dest_rect.h)
  a = np.radians(30)
  M = np.array([[np.cos(a), -np.sin(a)], [np.sin(a), np.cos(a)]])
  arrow = (
    (-0.9 * r, 0.5 * u),
    (0.6 * r, 0.5 * u),
    (0.6 * r, 1.65 * u),
    (r, 0.0),
    (0.6 * r, -1.65 * u),
    (0.6 * r, -0.5 * u),
    (-0.9 * r, -0.5 * u),
  ) @ M + (0.5 * dest_rect.w, 0.5 * dest_rect.h)
  pg.draw.polygon(surface, col, arrow, 0)


def draw_flat_tyre_icon(surface, dest_rect, col=None):
  if col is None: col = pg.Colour(255, 255, 255)
  u = max(1, int(round(min(dest_rect.w, dest_rect.h) / 20)))
  hu = 0.5 * u
  hw = 0.5 * (dest_rect.right - dest_rect.left)
  hh = 0.5 * (dest_rect.bottom - dest_rect.top)
  cx = dest_rect.left + hw
  cy = dest_rect.top + hh
  r = 0.97 * min(hw, hh) - hu
  k = np.radians(1)
  sidewall_top = np.array(
    [[np.cos(k * i), np.sin(k * i)] for i in range(180, 140, -5)]
  ) * 0.5 + (1.5 * np.cos(k * -45), 1.5 * np.sin(k * -45))
  sidewall = np.array(
    [[np.cos(k * i), np.sin(k * i)] for i in range(-45, 46, 5)]
  )
  sidewall_bot = np.array(
    [[np.cos(k * i), np.sin(k * i)] for i in range(225, 180, -5)]
  ) * 0.2 + (1.2 * np.cos(k * 45), 1.2 * np.sin(k * 45))
  sidewall = np.vstack((sidewall_top, sidewall, sidewall_bot))
  E = sidewall[-1]
  points1 = sidewall * r  + (cx, cy)
  points2 = sidewall * (-1, 1) * r  + (cx, cy)
  flat1 = points1[-1] + (0.8 * hu, 0)
  flat2 = points2[-1] + (-0.8 * hu, 0)
  pg.draw.lines(surface, col, False, points1, u)
  pg.draw.lines(surface, col, False, points2, u)
  pg.draw.line(surface, col, flat1, flat2, u)
  w = flat1[0] - flat2[0]
  n = 5
  mark = 3
  space = 2
  q = w / (n * (mark + space) - space)
  y = flat2[1] + 0.95 * u
  for i in range(n):
    x0 = flat2[0] + q * (mark + space) * i
    x1 = x0 + q * mark
    pg.draw.line(surface, col, (x0, y), (x1, y), u)
  s = max(1, 0.22 * r)
  R = pg.Rect((0, 0), (s, s))
  R.center = (cx, cy + 0.4 * r)
  pg.draw.rect(surface, col, R, 0)
  points = np.array([
    (-0.75 * u, -0.7 * r),
    (0.75 * u, -0.7 * r),
    (0.5 * u, 0.4 * r - 1.5 * s),
    (-0.5 * u, 0.4 * r - 1.5 * s),
  ]) + (cx, cy)
  pg.draw.polygon(surface, col, points, 0)


def draw_battery(surface, dest_rect, level):

  def draw_rect(R, rot270, col):
    if rot270:
      x = dest_rect.left + R.top
      y = dest_rect.bottom - R.right
      size = (R.height, R.width)
    else:
      x = dest_rect.left + R.left
      y = dest_rect.top + R.top
      size = R.size
    pg.draw.rect(surface, col, pg.Rect((x, y), size))

  def chix(level, base, irange):
    return max(0, min(255, int(round((level - base) * 255.0 / irange))))

  if dest_rect.w < dest_rect.h:
    T = pg.Rect((0, 0), (dest_rect.height, dest_rect.width))
    rot270 = True
  else:
    T = pg.Rect((0, 0), dest_rect.size)
    rot270 = False

  can_col = 0xFFFFFFFF
  u = max(1, T.h // 8)

  R = pg.Rect((0, 0), (T.w - u, u))
  R.topleft = T.topleft
  draw_rect(R, rot270, can_col)
  R.bottomleft = T.bottomleft
  draw_rect(R, rot270, can_col)
  R.size = (u, T.h)
  R.topleft = T.topleft
  draw_rect(R, rot270, can_col)
  R.topright = (T.right - u, T.top)
  draw_rect(R, rot270, can_col)
  s = max(0, 3 * T.h // 10)
  R.height = T.h - 2 * s
  R.topright = (T.right, T.top + s)
  draw_rect(R, rot270, can_col)

  w = int(round((T.w - 5 * u) * level))
  if w > 0:
    R.topleft = (2 * u, 2 * u)
    R.size = (w, T.h - 4 * u)
    if level >= 0.60:
      if level >= 0.9:
        level_col = pg.Color(0, 255, chix(level, 0.9, 0.1))
      else:
        level_col = pg.Color(0, 255, 0)
    else:
      if level >= 0.35:
        level_col = pg.Color(255 - chix(level, 0.35, 0.25), 255, 0)
      else:
        level_col = pg.Color(255, chix(level, 0.10, 0.25), 0)
    draw_rect(R, rot270, level_col)


def eval_bezier(C, t):
  while len(C) > 1:
    A = C[:-1]
    B = C[1:]
    C = (A + np.subtract(B, A) * t)
  return C[0]


def draw_portal(surface, view, mvm, radius=1.5, styles=None):

  dist = la.norm(mvm.matrix[3, :3] - view.pos)
  num_subdivs = int(round(max(5, min(20, 200 * radius / dist))))
  thickness = 0.3
  main_half_sweep = 4.0 / 6.0 * np.pi
  centre_z = radius * np.cos(main_half_sweep)
  mvm.push()
  mvm.translate((0.0, 0.0, -centre_z))
  arc_adjs = (
    (1.0, -0.5 * thickness),
    (1.0, 0.5 * thickness),
    (1.3, -0.5 * thickness),
    (1.3, 0.5 * thickness),
  )
  for rf, x in arc_adjs:
    r = rf * radius
    half_sweep = np.pi - np.arccos(-centre_z / r)
    half_segment_sweep = 0.5 * half_sweep
    foot_z = r * np.cos(half_sweep)
    foot_y = r * np.sin(half_sweep)
    cpr = r / np.cos(half_segment_sweep)
    mid_z = cpr * np.cos(half_segment_sweep)
    mid_y = cpr * np.sin(half_segment_sweep)
    mid_w = np.sin(0.5 * np.pi - half_segment_sweep)
    rat_curve = np.array([
      [x, foot_y, foot_z, 1.0],
      [x, mid_y, mid_z, mid_w],
      [x, 0.0, r, 1.0],
    ])
    w = np.atleast_2d(rat_curve[:, 3]).T
    homo_rat_curve = np.array(rat_curve)
    homo_rat_curve[:, :3] *= w
    if num_subdivs & 1:
      top_vertex = np.empty((0, 4))
      ls = np.linspace(0.0, 1.0 - 1 / num_subdivs, endpoint=True,
          num=max(1, 1 + num_subdivs//2))
    else:
      top_vertex = np.array([x, 0.0, r, 1.0])
      ls = np.linspace(0.0, 1.0, endpoint=False,
          num=max(1, 1 + num_subdivs//2))
    vertices1 = np.array([eval_bezier(homo_rat_curve, t) for t in ls])
    vertices2 = np.flip(vertices1 @ np.diag((1, -1, 1, 1)), (0,))
    vertices = np.vstack((vertices1, top_vertex, vertices2))
    col = 0xFFAA00
    lw = 1
    if styles is not None:
      if styles[0] is not None: col = styles[0]
      if styles[1] is not None: lw = styles[1]
    pe = view.project_to_eye_space(vertices, mvm.matrix)
    edge_run = tuple(range(len(pe)))
    C = view.clipped_edge_run_vertices(pe, [edge_run])
    S = view.project_es_to_screen(C)
    for i in range(0, len(S), 2):
      pg.draw.line(surface, col, S[i], S[i + 1], width=lw)
  mvm.pop()


sinclair_c5000_props = {
  'name': "Sinclair C5000",
  'max_wheel_speed': 100.0 / 3.6,  # m/s
  'throttle_factor': 0.05,
  'cruise_mal': MotorAccLimits.full(
    facc=4.0, fdec=4.0, racc=4.0, rdec=4.0, jerk=10.0
  ),
  'braking_mal': MotorAccLimits(10.0, jerk=100.0),
  'wheel_mal': MotorAccLimits.full(
    facc=7.0, fdec=7.0, racc=7.0, rdec=7.0, jerk=20.0
  ),
  'max_turn_rate': np.radians(60),
  'max_tc_knob_vel': 10,
  'max_tc_knob_acc': 30,
  'max_lat_accel': 4.0,
  'reversing_omega_slope': 0.5,  #d(omega)/dv implies turn circle radius.
  'jog_factor': 0.1,
  'turn_jog_factor': 0.1,
  'draw_fn': draw_sinclair_c5000,
  'draw_fn_styles': (pg.Color(240, 0, 0), 2),
  'traction_offset': np.array([-0.05, 0.0, -0.2]),
  'driver_offset': np.array([0.05, 0.0, 0.8]),
  'axle_width': 0.55,
  'wheel_radius': 0.25,
  'wheel_width': 0.2,
  'std_view_dist': 4.5,
}

sinclair_c50_props = {
  'name': "Sinclair C50",
  'max_wheel_speed': 15.0 / 3.6,  # m/s
  'throttle_factor': 0.1,
  'cruise_mal': MotorAccLimits.full(
    facc=2.0, fdec=2.0, racc=2.0, rdec=2.0, jerk=10.0
  ),
  'braking_mal': MotorAccLimits(7.0, jerk=60.0),
  'wheel_mal': MotorAccLimits.full(
    facc=3.0, fdec=3.0, racc=3.0, rdec=3.0, jerk=20.0
  ),
  'max_turn_rate': np.radians(60),
  'max_tc_knob_vel': 10,
  'max_tc_knob_acc': 30,
  'max_lat_accel': 4.0,
  'reversing_omega_slope': 0.5,  #d(omega)/dv implies turn circle radius.
  'jog_factor': 0.1,
  'turn_jog_factor': 0.1,
  'draw_fn': draw_sinclair_c5000,
  'draw_fn_styles': (pg.Color(0, 200, 255), 2),
  'traction_offset': np.array([-0.05, 0.0, -0.2]),
  'driver_offset': np.array([0.05, 0.0, 0.8]),
  'axle_width': 0.55,
  'wheel_radius': 0.25,
  'wheel_width': 0.2,
  'std_view_dist': 4.5,
}

fast_artcar_props = {
  'name': "Fast Art Car",
  'max_wheel_speed': 160.0 / 3.6,  # m/s
  'throttle_factor': 0.04,
  'cruise_mal': MotorAccLimits.full(
    facc=5.0, fdec=5.0, racc=5.0, rdec=5.0, jerk=15.0
  ),
  'braking_mal': MotorAccLimits(10.0, jerk=50.0),
  'wheel_mal': MotorAccLimits.full(
    facc=12.0, fdec=12.0, racc=12.0, rdec=12.0, jerk=60.0
  ),
  'max_turn_rate': np.radians(60),
  'max_tc_knob_vel': 10,
  'max_tc_knob_acc': 30,
  'max_lat_accel': 5.0,
  'reversing_omega_slope': 0.6,  #d(omega)/dv implies turn circle radius.
  'jog_factor': 0.02,
  'turn_jog_factor': 0.3,
  'draw_fn': draw_artcar1,
  'draw_fn_styles': (pg.Color(90, 0, 180), 2),
  'traction_offset': np.array([0.0, 0.0, -0.3]),
  'driver_offset': np.array([1.15, 0.0, 1.75]),
  'axle_width': 2.5,
  'wheel_radius': 0.480,
  'wheel_width': 0.285,
  'std_view_dist': 12.0,
}

artcar1_props = {
  'name': "Art Car 1",
  'max_wheel_speed': 8.0 / 3.6,  # m/s
  'throttle_factor': 0.1,
  'cruise_mal': MotorAccLimits.full(
    facc=0.5, fdec=0.5, racc=0.5, rdec=0.5, jerk=5.0
  ),
  'braking_mal': MotorAccLimits(2.0, jerk=12.0),
  'wheel_mal': MotorAccLimits.full(
    facc=1.0, fdec=0.7, racc=1.0, rdec=0.7, jerk=15.0
  ),
  'max_turn_rate': np.radians(20),
  'max_tc_knob_vel': 3,
  'max_tc_knob_acc': 5,
  'max_lat_accel': 4.0,
  'reversing_omega_slope': 0.4,  #d(omega)/dv implies turn circle radius.
  'jog_factor': 0.2,
  'turn_jog_factor': 0.2,
  'draw_fn': draw_artcar1,
  'draw_fn_styles': (pg.Color(0, 160, 200), 2),
  'traction_offset': np.array([0.0, 0.0, -0.3]),
  'driver_offset': np.array([1.15, 0.0, 1.75]),
  'axle_width': 2.5,
  'wheel_radius': 0.480,
  'wheel_width': 0.285,
  'std_view_dist': 12.0,
}


vehicles_props = [
  artcar1_props,
  fast_artcar_props,
  sinclair_c50_props,
  sinclair_c5000_props,
]


def main():

  #prog_dir = os.path.split(os.path.abspath(__file__))[0]

  ser = None
  ser_dev_name = "/dev/ttyUSB0"
  try:
    ser = serial.Serial(ser_dev_name, 115200, timeout=1)
  except serial.SerialException as E:
    print("No serial port \"{}\":\n{}".format(ser_dev_name, str(E)))
  serbuf = bytes()
  ser_lm = 0.0
  ser_rm = 0.0
  ser_lamps = 0x00
  ser_buttons = 0x00000

  pg.init()
  clock = pg.time.Clock()

  # Requested screen size
  rss = (1280, 960)
  #rss = (640, 480)

  window_style = 0  # FULLSCREEN
  best_depth = pg.display.mode_ok(rss, window_style, 32)
  screen = pg.display.set_mode(rss, window_style, best_depth)
  screen_size = screen.get_width(), screen.get_height()
  pg.display.set_caption("Motor Control Wotsit.")

  mouse_joy_gain = 2.0
  pov_mode = ViewMode(0)
  current_vehicle_ix = -1
  requested_vehicle_ix = 0
  playground_level = 1
  grid_mode = 3
  reverse_turns = False
  limit_turn_rate = True
  enable_joy_brake = False
  soften_speed = True
  soften_turns = True
  enable_throttle = True
  motors_are_magic = False
  max_trim = 0.05
  mistrim = 0.0
  trim = 0.0
  trim_v = 0.0
  zeroing_trim = False
  trimming = False
  use_experimental_ctrl = False
  joydump = False

  fixed_cam_pos = np.array([0.0, -3.0, 1.2])

  dummy_mal = MotorAccLimits(0.1, jerk=1.0)
  speed_ctrl = CarSpeedCtrl(dummy_mal, dummy_mal)
  turn_ctrl = QPosCtrl()
  turn_caps = TurnCaps()
  lw_ctrl = SpeedCtrl(dummy_mal)
  rw_ctrl = SpeedCtrl(dummy_mal)
  pv = RoboMouse()
  pv.plonk([2.5, -0.25, 0.0], np.radians(30.0))

  avail_idms_set = {InputDeviceMode.MOUSE}
  default_idm = InputDeviceMode.MOUSE
  gamepad_bat_level = -1.0
  gamepad = None
  gpmap = None

  if pg.joystick.get_init():
    jsc = pg.joystick.get_count()
    if jsc > 0:
      print(f"{jsc} Joystick(s) found.")
      js = pg.joystick.Joystick(0)
      na = js.get_numaxes()
      nb = js.get_numbuttons()
      nh = js.get_numhats()
      nballs = js.get_numballs()
      guid_str = js.get_guid()
      print("Joystick: {}".format(js.get_name()))
      print(f"{na} axes, {nb} buttons, {nh} hats, {nballs} trackballs")
      print(f"GUID of controller in SDL:\n{guid_str}")
      if na >= 2:
        gamepad = js
        avail_idms_set |= {InputDeviceMode.JOYSTICK_ISO}
        default_idm = InputDeviceMode.JOYSTICK_ISO
        if na >= 4:
          avail_idms_set |= {InputDeviceMode.JOYSTICKS_VH}
          avail_idms_set |= {InputDeviceMode.JOYSTICKS_HPAT}
          default_idm = InputDeviceMode.JOYSTICKS_VH
        name, mapping_str = find_known_gamepad(guid_str, known_gamepads)
        if mapping_str:
          print(f"Found mapping for \"{name}\".")
        else:
          print(f"Button and Axes mappings are unknown. Assuming PS3.")
          mapping_str = "leftx:a0,lefty:a1"
          if na >= 4:
            mapping_str = "leftx:a0,lefty:a1,rightx:a2,righty:a3"
          if na >= 6:
            mapping_str = ("leftx:a0,lefty:a1,rightx:a3,righty:a4,"
                           "lefttrigger:a2,righttrigger:a5")
          if nb >= 4:
            mapping_str += ",a:b0,b:b1,x:b3,y:b2"
          if nb >= 6:
            mapping_str += ",leftshoulder:b4,rightshoulder:b5"
          if nb >= 13:
            mapping_str += (",back:b8,start:b9,guide:b10"
                            ",leftstick:b11,rightstick:b12")
          if nb >= 17:
            mapping_str += ",dpup:b13,dpdown:b14,dpleft:b15,dpright:b16"
        gpmap = GamepadMapping(mapping_str)
      else:
        print("A joystick with fewer than two axes is useless!")
    else:
      print("No joystick found.")
  avail_idms = list(avail_idms_set)
  idm_ix = avail_idms.index(default_idm)

  jw = int(round(min(0.15 * screen_size[0], 0.25 * screen_size[1])))
  jh = jw
  scr_margin = int(round(jw / 10))
  gutter = int(round(jw / 15))
  instr_top = screen_size[1] - scr_margin - jh
  instr_bg_col = pg.Color(0, 0, 0, 110)
  instr_icon_alphas = (120, 255)

  # XY joystick
  joy_rect = pg.Rect((scr_margin, instr_top), (jw, jh))
  joy_surface = pg.Surface(joy_rect.size, pg.SRCALPHA, screen)
  lw = int(round(0.3 * jw))

  # BZT levers
  x = joy_rect.left + 0.5 * jw
  llev_rect = pg.Rect((x - 0.5 * gutter - lw, instr_top), (lw, jh))
  llev_surface = pg.Surface(llev_rect.size, pg.SRCALPHA, screen)
  rlev_rect = pg.Rect((llev_rect.right + gutter, instr_top), (lw, jh))
  rlev_surface = pg.Surface(rlev_rect.size, pg.SRCALPHA, screen)

  # Separate vertical and horizontal levers
  x = scr_margin + 0.5 * (jw - lw)
  vtop = instr_top - gutter - lw
  vlev_rect = pg.Rect((x, vtop), (lw, jh))
  vlev_surface = pg.Surface(vlev_rect.size, pg.SRCALPHA, screen)
  hlev_rect = pg.Rect((scr_margin, vtop + gutter + jh), (jw, lw))
  hlev_surface = pg.Surface(hlev_rect.size, pg.SRCALPHA, screen)

  # Steerng wheel indicator
  wiw = int(round(0.15 * jw))
  swi_rect = pg.Rect((0, 0), (wiw, wiw))
  swi_surface = pg.Surface(swi_rect.size, pg.SRCALPHA, screen)
  swi_col = pg.Color(0, 100, 160)
  draw_steering_wheel_icon(swi_surface, swi_rect, swi_col)

  # Input moderator indicator
  imiw = int(round(0.25 * jw))
  imi_rect = pg.Rect((0, 0), (imiw, imiw))
  im0i_surface = pg.Surface(imi_rect.size, pg.SRCALPHA, screen)
  im1i_surface = pg.Surface(imi_rect.size, pg.SRCALPHA, screen)
  im2i_surface = pg.Surface(imi_rect.size, pg.SRCALPHA, screen)
  imi_col = pg.Color(0, 100, 160)
  draw_im_icon(im0i_surface, imi_rect, 0, imi_col)
  draw_im_icon(im1i_surface, imi_rect, 1, imi_col)
  draw_im_icon(im2i_surface, imi_rect, 2, imi_col)
  imi_rect.midleft = joy_rect.midright
  imi_rect.left += gutter

  # Magic motor indicator
  miw = int(round(0.25 * jw))
  mmi_rect = pg.Rect((0, 0), (miw, miw))
  mmi_surface = pg.Surface(mmi_rect.size, pg.SRCALPHA, screen)
  mmi_col = pg.Color(0, 100, 160)
  draw_motor_icon(mmi_surface, mmi_rect, mmi_col, magic=True)
  mmi_rect.centerx = imi_rect.centerx
  mmi_rect.top = imi_rect.bottom + 0.5 * gutter

  # Throttle indicator
  tiw = int(round(0.22 * jw))
  ti_rect = pg.Rect((0, 0), (tiw, tiw))
  ti_surface = pg.Surface(ti_rect.size, pg.SRCALPHA, screen)
  ti_col = pg.Color(0, 100, 160)
  draw_throttle_icon(ti_surface, ti_rect, ti_col)
  ti_rect.centerx = imi_rect.centerx
  ti_rect.bottom = imi_rect.top - 0.5 * gutter

  # Flat tyre indicator
  ftiw = int(round(0.22 * jw))
  fti_rect = pg.Rect((0, 0), (ftiw, ftiw))
  fti_surface = pg.Surface(fti_rect.size, pg.SRCALPHA, screen)
  fti_col = pg.Color(0, 100, 160)
  draw_flat_tyre_icon(fti_surface, fti_rect, fti_col)
  fti_rect.right = screen_size[0] - scr_margin
  fti_rect.bottom = joy_rect.bottom

  # Wheel trim gauge
  wt_rect = pg.Rect((0, 0), (1.5 * jw, lw))
  wt_rect.bottom = fti_rect.bottom
  wt_rect.right = fti_rect.left - gutter
  wt_surface = pg.Surface(wt_rect.size, pg.SRCALPHA, screen)

  # Soft control gauges
  scgauges_rect = pg.Rect(
    (imi_rect.right + gutter, instr_top),
    (0.6 * jw, jh),
  )
  scgauges_surface = pg.Surface(scgauges_rect.size, pg.SRCALPHA, screen)

  # Turn rate gauge
  tr_rect = pg.Rect((scgauges_rect.left, 0), (scgauges_rect.w, lw))
  tr_rect.bottom = instr_top
  tr_surface = pg.Surface(tr_rect.size, pg.SRCALPHA, screen)

  # Brake gauge
  brake_rect = pg.Rect((0, 0), (lw, 2 * scgauges_rect.h // 3))
  brake_rect.left = scgauges_rect.right + gutter
  brake_rect.bottom = scgauges_rect.bottom
  brake_surface = pg.Surface(brake_rect.size, pg.SRCALPHA, screen)

  # Joy brake indicator
  jbiw = int(round(0.25 * jw))
  jbi_rect = pg.Rect((0, 0), (jbiw, jbiw))
  jbi_surface = pg.Surface(jbi_rect.size, pg.SRCALPHA, screen)
  jbi_col = pg.Color(0, 100, 160)
  draw_joy_brake_icon(jbi_surface, jbi_rect, jbi_col)
  jbi_rect.left = brake_rect.left + 0.1 * lw
  jbi_rect.bottom = brake_rect.top

  mvm = ModelviewMtxStack()

  view = Perspective(screen_size, 90.0, near=0.01)
  view.sense = VIEW_SENSE_LAND_VEHICLE
  view.pos = np.array([-0.5, -4.5, 2.5])
  view.look_at(np.array([0, 0, 0]), np.array([0,0,1]))
  view.update()

  std_view_dist = 100.0
  vd_ctrl = QPosCtrl()
  vd_ctrl.target_x = 1.0 / std_view_dist
  vd_ctrl.x = 1.0 / (50.0 * std_view_dist)
  vd_ctrl.v = 0.0
  vd_ctrl.max_fwd_v = vd_ctrl.max_rev_v = 0.2
  vd_ctrl.max_a = 0.5

  anim_counter = 0
  max_fps = 100
  dampened_fps = max_fps
  delta_time = 1.0 / max_fps

  do_exit = False

  while not do_exit:

    for event in pg.event.get():
      if event.type == pg.QUIT:
        do_exit = True
        print("[Quit]")
      elif event.type == pg.KEYUP and event.key == pg.K_ESCAPE:
        do_exit = True
        print("[ESC] Quit")
      elif event.type == pg.KEYUP:
        if event.key == pg.K_q:
          do_exit = True
          print("[Q] Quit")
      elif event.type == pg.KEYDOWN:
        if event.key == pg.K_h:
          pv.plonk([0, 0], np.radians(90.0))
          print("[H] Home")
        elif event.key == pg.K_p:
          playground_level = (playground_level + 1) % 3
          print("[P] Playground level {}".format(playground_level))
        elif event.key == pg.K_v or event.key == pg.K_f:
          dx = 2.0 * std_view_dist
          dy = random.randrange(-1, 4, 1) * 0.2 * std_view_dist
          dz = (0.04, 0.2, 0.5)[random.randrange(3)] * std_view_dist
          fixed_cam_pos = np.array(pv.pos)
          fixed_cam_pos += np.array([dx, dy, dz]) @ pv.ori
          if event.key == pg.K_f:
            pov_mode = ViewMode.REMOTE
          else:
            pov_mode = ViewMode((pov_mode + 1) % len(ViewMode))
            vd_ctrl.x = vd_ctrl.target_x = 1.0 / std_view_dist
          print("[V] View: {}".format(pov_mode.name))
        elif event.key == pg.K_i:
          idm_ix = (idm_ix + 1) % len(avail_idms)
          print("[I] Input method: {}".format(avail_idms[idm_ix].name))
        elif event.key == pg.K_g:
          grid_mode = (grid_mode + 1) % 6
          if grid_mode:
            print("[G] Grid {}".format(grid_mode))
          else:
            print("[G] No grid")
        elif event.key == pg.K_w:
          reverse_turns = not reverse_turns
          if reverse_turns:
            print("[W] Steering wheel mode: Stick towards centre of turn")
          else:
            print("[W] ISO steering mode")
        elif event.key == pg.K_a:
          limit_turn_rate = not limit_turn_rate
          if limit_turn_rate:
            print("[A] Turn rate is limited according to g-force.")
          else:
            print("[A] Turn rate limit disregards lateral g-force.")
        elif event.key == pg.K_s:
          soften_speed = not soften_speed
          if soften_speed:
            print("[S] Using speed controller")
          else:
            print("[S] Bypassing speed controller")
        elif event.key == pg.K_d:
          soften_turns = not soften_turns
          if soften_turns:
            print("[D] Turn damper enabled")
          else:
            print("[D] Turns damper disabled: Only motors dampen turns.")
        elif event.key == pg.K_j:
          enable_joy_brake = not enable_joy_brake
          speed_ctrl.enable_joy_brake = enable_joy_brake
          speed_ctrl.joy_braking_state = 0
          if enable_joy_brake:
            print("[J] Reversing joystick activates brake")
          else:
            print("[J] Joystick brake disabled: Use trigger.")
        elif event.key == pg.K_t:
          enable_throttle = not enable_throttle
          if enable_throttle:
            print("[T] Throttle enabled for speed controller.")
          else:
            print("[T] Speed controller operates without throttle.")
        elif event.key == pg.K_m:
          motors_are_magic = not motors_are_magic
          if motors_are_magic:
            print("[M] Motors are magic.")
          else:
            print("[M] Motors have acceleration limits.")
        elif event.key == pg.K_l:
          if mistrim:
            mistrim = 0.0
            print("[L] Tyres are equally inflated.")
          else:
            x = random.choice((10, 20, 30))
            s = random.choice((-1, 1))
            mistrim = 0.001 * s * x
            print("[L] Flat tyre: Mistrim =", mistrim)
        elif event.key == pg.K_y and gamepad is not None:
          joydump = not joydump
          if joydump:
            print("[Y] Joystick dump:")
          else:
            print("[Y] Joystick dump disabled")
        elif event.key == pg.K_x:
          use_experimental_ctrl = not use_experimental_ctrl
          if use_experimental_ctrl:
            print("[X] Experimental control layout active")
          else:
            print("[X] Normal control layout active")
        elif event.key == pg.K_c:
          requested_vehicle_ix += 1
          print("[C] Fetching new car...")

    requested_vehicle_ix = requested_vehicle_ix % len(vehicles_props)
    if requested_vehicle_ix != current_vehicle_ix:
      props = vehicles_props[requested_vehicle_ix]
      name = props.get('name', "Untitled")
      print("New vehicle:", name)
      max_wheel_speed = props['max_wheel_speed']
      max_body_speed = max_wheel_speed  # Will be automatically limited.
      throttle_factor = props['throttle_factor']
      jog_factor = props['jog_factor']
      turn_jog_factor = props['turn_jog_factor']
      speed_ctrl.cruise_mal = props['cruise_mal']
      speed_ctrl.braking_mal = props['braking_mal']
      speed_ctrl.throttle_factor = throttle_factor if enable_throttle else 1.0
      turn_ctrl.max_fwd_v = turn_ctrl.max_rev_v = props['max_tc_knob_vel']
      turn_ctrl.max_a = props['max_tc_knob_acc']
      pv.axle_width = props['axle_width']
      max_bzt_omega = 2.0 * max_wheel_speed / pv.axle_width
      turn_caps.max_lat_accel = props['max_lat_accel']
      turn_caps.max_turn_rate = props['max_turn_rate']
      turn_caps.reversing_omega_slope = props['reversing_omega_slope']
      turn_caps.max_turn_rate = min(turn_caps.max_turn_rate, max_bzt_omega)
      mbs_too_high = True
      while mbs_too_high:
        mbs_too_high = False
        omega = turn_caps.max_turn_rate_for_speed(max_body_speed)
        hds = 0.5 * omega * pv.axle_width
        if max_body_speed + hds > max_wheel_speed:
          new_max_body_speed = max_wheel_speed - hds
          if new_max_body_speed < max_body_speed:
            max_body_speed = new_max_body_speed
            mbs_too_high = True
          print("New max body speed = {} m/s".format(max_body_speed))
      #max_body_speed = 0.6 * max_wheel_speed; print("Overriden!") #<<<<<<<<<<<
      lw_ctrl.mal = rw_ctrl.mal = props['wheel_mal']
      pv.draw_fn = props['draw_fn']
      pv.draw_fn_styles = props['draw_fn_styles']
      pv.traction_offset = props['traction_offset']
      pv.driver_offset = props['driver_offset']
      pv.lw_state.radius = pv.rw_state.radius = props['wheel_radius']
      pv.lw_state.width = pv.rw_state.width = props['wheel_width']
      pv.plonk(pv.pos, None)
      std_view_dist = props['std_view_dist']
      vd_ctrl.target_x = 1.0 / std_view_dist
      current_vehicle_ix = requested_vehicle_ix

    if ser is not None:
      if ser.in_waiting > 0:
        serbuf += ser.read(ser.in_waiting)
        lines = serbuf.split(b"\n")
        if len(lines) >= 2:
          for line in lines[:-1]:
            L = line.strip().decode('ascii')
            a = 0
            for c in L:
              x = -1
              if 'A' <= c <= 'Z':
                x = ord(c) - ord('A')
              elif 'a' <= c <= 'z':
                x = ord(c) - ord('a') + 26
              elif '0' <= c <= '9':
                x = ord(c) - ord('0') + 52
              elif c == '+':
                x = 62
              elif c == '/':
                x = 63
              if x >= 0:
                a = (a << 6) + x
              else:
                a = -1
                break
            if a >= 0:
              x = ((a >> 12) & 0xFFF)
              if x >= 0x800: x -= 0x1000
              ser_lm = np.clip(float(x) / 2047.0, -1.0, +1.0)
              x = ((a >> 0) & 0xFFF)
              if x >= 0x800: x -= 0x1000
              ser_rm = np.clip(float(x) / 2047.0, -1.0, +1.0)
              ser_lamps = (a >> 24) & 0x3F
              ser_buttons = (a >> 30) & 0x3FFFF
            #BBBILLRR
            print("{}: {:018b} {:06b} {:7.3f} {:7.3f}"
              .format(L, ser_buttons, ser_lamps, ser_lm, ser_rm))
          serbuf = lines[-1]

    keystate = pg.key.get_pressed()
    mouse_pos = pg.mouse.get_pos()
    aspect = (screen_size[0] - 1) / (screen_size[1] - 1)
    mx = (mouse_pos[0] / (screen_size[0] - 1))
    my = (mouse_pos[1] / (screen_size[1] - 1))

    idm = avail_idms[idm_ix]
    num_js_axes = 0
    num_js_buttons = 0
    if gamepad is not None:
      num_js_axes = gamepad.get_numaxes()
      num_js_buttons = gamepad.get_numbuttons()

    speed_ctrl.enable_joy_brake = enable_joy_brake
    turn_caps.reverse_turns = reverse_turns
    max_ctrl_speed = max_body_speed
    max_omega = turn_caps.max_turn_rate
    if idm == InputDeviceMode.JOYSTICKS_HPAT and not limit_turn_rate:
      max_ctrl_speed = max_wheel_speed
      max_omega = max_bzt_omega
    max_omega_for_speed = max_omega

    real_joy_slop_hw = 0.043
    joystick = np.zeros(2)
    bztj_left = 0.0
    bztj_right = 0.0
    mbztj_left = 0.0
    mbztj_right = 0.0

    l_trigger = 0.0
    r_trigger = 0.0
    if idm != InputDeviceMode.MOUSE:
      l_trigger = 0.5 * (gpmap.axis(gamepad, GamepadAxis.LEFTTRIGGER) + 1.0)
      r_trigger = 0.5 * (gpmap.axis(gamepad, GamepadAxis.RIGHTTRIGGER) + 1.0)
      l_trigger = np.clip(1.05 * l_trigger - 0.05, 0.0, 1.0)
      r_trigger = np.clip(1.05 * r_trigger - 0.05, 0.0, 1.0)
    if idm != InputDeviceMode.MOUSE:
      was_trimming = trimming
      trim_btn_pressed = gpmap.btn(gamepad, GamepadBtn.B)
      if trim_btn_pressed or zeroing_trim:
        trimming = True
      if trimming:
        if zeroing_trim:
          if trim == 0.0 and trim_v == 0.0:
            if l_trigger == 0.0 and r_trigger == 0.0:
              zeroing_trim = False
        else:
          trim_v = 0.005 * (l_trigger - r_trigger)
          if l_trigger >= 0.8 and r_trigger >= 0.8:
            zeroing_trim = True
          if l_trigger == 0.0 and r_trigger == 0.0 and not trim_btn_pressed:
            trimming = False
        l_trigger = 0.0
        r_trigger = 0.0
      else:
        trim_v = 0.0
      if trimming != was_trimming:
        if trimming:
          print("(Circle/B) Triggers adjust trim.")
        else:
          print("Triggers apply breakes.")

    if idm == InputDeviceMode.JOYSTICKS_HPAT:
      bztj_left = sloppy_joy(
        -gpmap.axis(gamepad, GamepadAxis.LEFTY),
        real_joy_slop_hw,
      )
      bztj_right = sloppy_joy(
        -gpmap.axis(gamepad, GamepadAxis.RIGHTY),
        real_joy_slop_hw,
      )
      joystick[:] = joy_vv2xy(bztj_left, bztj_right)
      #print('BZT', bztj_left, bztj_right)
      #print('Joy0 {:<5.3f} {:<5.3f}'.format(*joystick))
      if limit_turn_rate:
        k = 1.0 # max_bzt_omega / max_omega
        joystick[0] = np.clip(k * joystick[0], -1.0, +1.0)
      turn_caps.reverse_turns = False
      #print('Joy1 {:<5.3f} {:<5.3f}'.format(*joystick))
    elif idm == InputDeviceMode.JOYSTICK_ISO:
      joystick = np.array([
        sloppy_joy(
          gpmap.axis(gamepad, GamepadAxis.LEFTX),
          real_joy_slop_hw,
        ),
        sloppy_joy(
          -gpmap.axis(gamepad, GamepadAxis.LEFTY),
          real_joy_slop_hw,
        ),
      ])
    elif idm == InputDeviceMode.JOYSTICKS_VH:
      joystick = np.array([
        sloppy_joy(
          gpmap.axis(gamepad, GamepadAxis.RIGHTX),
          real_joy_slop_hw,
        ),
        sloppy_joy(
          -gpmap.axis(gamepad, GamepadAxis.LEFTY),
          real_joy_slop_hw,
        ),
      ])
    else:
      # Fall back to InputDeviceMode.MOUSE
      joystick = np.array((-1.0 + 2.0 * mx, 1.0 - 2.0 * my))
      if aspect > 1.0: joystick[0] *= aspect
      if aspect < 1.0: joystick[1] /= aspect
      joystick[0] = sloppy_joy(joystick[0])
      joystick[1] = sloppy_joy(joystick[1])
      joystick = np.clip(mouse_joy_gain * joystick, -1.0, +1.0)

    speed_ctrl.throttle_factor = throttle_factor if enable_throttle else 1.0
    is_jogging = False
    if gpmap is not None:
      dup = gpmap.btn(gamepad, GamepadBtn.DPAD_UP)
      ddn = gpmap.btn(gamepad, GamepadBtn.DPAD_DOWN)
      dle = gpmap.btn(gamepad, GamepadBtn.DPAD_LEFT)
      dri = gpmap.btn(gamepad, GamepadBtn.DPAD_RIGHT)
      hy = (0, 1)[dup] - (0, 1)[ddn]
      hx = (0, 1)[dri] - (0, 1)[dle]
      if (hx, hy) != (0, 0):
        # Jog mode via hat/D-pad
        turn_caps.reverse_turns = False
        speed_ctrl.enable_joy_brake = False
        speed_ctrl.joy_braking_state = 0
        joystick[0] = hx * turn_jog_factor
        joystick[1] = hy * jog_factor
        is_jogging = True
    if use_experimental_ctrl and not is_jogging:
      trig_jog_thres = 0.1
      lt1 = l_trigger
      rt1 = r_trigger
      if True:
        lt1 = 1.0 - lt1
        rt1 = 1.0 - rt1
      lt2 = (lt1 - trig_jog_thres) * (1.0 / (1.0 - trig_jog_thres))
      rt2 = (rt1 - trig_jog_thres) * (1.0 / (1.0 - trig_jog_thres))
      if lt2 > 0.0:
        joystick[1] *= (1.0 - (1.0 - jog_factor) * lt2)
      if rt2 > 0.0:
        joystick[0] *= (1.0 - (1.0 - turn_jog_factor) * rt2)

    soft_joy = np.array(joystick)
    turn_ctrl.target_x = joystick[0]
    if not soften_turns:
      turn_ctrl.x = turn_ctrl.target_x
      turn_ctrl.v = 0.0
    soft_joy[0] = turn_ctrl.x

    actual_speed = speed_ctrl.current_speed  # <<< Honest, Guv!
    actual_speed = 0.5 * (lw_ctrl.current_speed + rw_ctrl.current_speed)

    cmd_speed = max_ctrl_speed * soft_joy[1]
    if limit_turn_rate:
      max_omega_for_speed = turn_caps.max_turn_rate_for_speed(actual_speed)
    omega = -max_omega_for_speed * soft_joy[0]
    half_diff_speed = 0.5 * omega * pv.axle_width
    mbztj_left = (cmd_speed - half_diff_speed) / max_wheel_speed
    mbztj_right = (cmd_speed + half_diff_speed) / max_wheel_speed
    mbztj_left = np.clip(mbztj_left, -1.0, +1.0)
    mbztj_right = np.clip(mbztj_right, -1.0, +1.0)
    # ~ ql = int(round(12 * 0.5 * (mbztj_left + 1.0)))
    # ~ sl = "#" * ql + "-" * (12 - ql)
    # ~ qr = int(round(12 * 0.5 * (mbztj_right + 1.0)))
    # ~ sr = "#" * qr + "-" * (12 - qr)
    # ~ print(sl, sr)
    # ~ print(mbztj_left, mbztj_right)

    if not use_experimental_ctrl:
      bf = max(l_trigger, r_trigger)
    speed_ctrl.input_braking_factor = bf
    speed_ctrl.lever_pos = soft_joy[1]
    speed_ctrl.max_speed = max_ctrl_speed
    #speed_ctrl.current_speed = actual_speed
    speed_ctrl.animate()
    if not soften_speed:
      speed_ctrl.target_speed = soft_joy[1] * max_ctrl_speed * (1.0 - bf)
      speed_ctrl.current_speed = speed_ctrl.target_speed
      speed_ctrl.v_pos_ctrl.x = speed_ctrl.target_speed
      speed_ctrl.v_pos_ctrl.target_x = speed_ctrl.target_speed
      speed_ctrl.v_pos_ctrl.v = 0.0
    half_diff_speed = 0.5 * pv.axle_width * omega  #<<< redundant?
    lw_ctrl.target_speed = speed_ctrl.current_speed - half_diff_speed
    rw_ctrl.target_speed = speed_ctrl.current_speed + half_diff_speed
    if ser is not None:
      lw_ctrl.target_speed = ser_lm * max_wheel_speed
      rw_ctrl.target_speed = ser_rm * max_wheel_speed
    lw_ctrl.animate()
    rw_ctrl.animate()

    a = speed_ctrl.current_accel;
    bf_thres = 0.05
    if actual_speed < 0.0: a = -a
    if a < -0.5 or speed_ctrl.joy_braking_state != 0 or bf >= bf_thres:
      pv.stop_lamp_lit = True
    if a >= -0.01 and speed_ctrl.joy_braking_state == 0 and bf < bf_thres:
      pv.stop_lamp_lit = False

    if num_js_buttons >= 6:
      ldi = gpmap.btn(gamepad, GamepadBtn.LEFTSHOULDER)
      rdi = gpmap.btn(gamepad, GamepadBtn.RIGHTSHOULDER)
      pv.blinkers.input = (ldi << 1) + rdi
    pv.blinkers.animate()

    lw_trim_factor = max(0.0, min(1.0, 1.0 - (mistrim + trim)))
    rw_trim_factor = max(0.0, min(1.0, 1.0 + (mistrim + trim)))

    # Render stuff

    screen.fill((0, 0, 0))
    C = pv.pos + np.array([0.0, 0.0, 0.5])
    d = 1.0 / vd_ctrl.x
    if pov_mode == ViewMode.HIGH_LOOK_N:
      view.pos = C + np.array([0.0, 0.0, 2 * d])
      view.look_at(pv.pos, np.array([0.0, 1.0, 0.0]))
    elif pov_mode == ViewMode.ARSE:
      phi = np.radians(26)
      dx = -d * np.cos(phi)
      dz = d * np.sin(phi)
      view.pos = C + dx * pv.ori[0] + np.array([0.0, 0.0, dz])
      view.look_at(pv.pos, np.array([0, 0, 1.0]))
    elif pov_mode == ViewMode.DRIVER:
      view.pos = pv.pos + pv.driver_offset @ pv.ori
      view.ori = pv.ori
    elif pov_mode == ViewMode.REMOTE:
      view.pos = fixed_cam_pos
      view.look_at(C, np.array([0.0, 0.0, 1.0]))
    else:
      phi = np.radians(26)
      view.pos = C + np.array([0.0, -d * np.cos(phi), d * np.sin(phi)])
      view.look_at(pv.pos, np.array([0.0, 0.0, 1.0]))
    view.update()

    draw_ground_grid(screen, view, mvm, C, grid_mode)
    draw_world_basis_vectors(screen, view, mvm)

    portals = (
     ((0, 4), 0, 4.0, (0xFFCC00, 1)),
     ((6, 0), -45, 1.5, (0x00CC99, 1)),
     ((4.5, -3.5), 87, 1.0, (0xFF7777, 1)),
     ((12, -3.5), 90, 1.0, (0xFF7777, 1)),
     ((15, -6.5), 180, 1.0, (0xFF7777, 1)),
     ((15, -15), 180, 1.0, (0xFF7777, 1)),
     ((12, -18), 270, 1.0, (0xFF7777, 1)),
     ((4, -18), 270, 1.0, (0xFF7777, 1)),
     ((-4, -18), 270, 1.0, (0xFF7777, 1)),
     ((-7, -21), 180, 1.0, (0xFF7777, 1)),
     ((-15, 0), 0, 1.4, (0xFF0000, 1)),
     ((-15, 3), 0, 1.4, (0xFF7700, 1)),
     ((-15, 6), 0, 1.4, (0xFFEE00, 1)),
     ((-15, 9), 0, 1.4, (0x00AA00, 1)),
     ((-15, 12), 0, 1.4, (0x0000FF, 1)),
     ((-8, -15), 350, 2.0, (0xFFFF00, 1)),
     ((-7, 18), 80, 2.0, (0x0088FF, 1)),
     ((-0, 18), 100, 2.0, (0x0088FF, 1)),
     ((0, -30), 0, 1.5, (0xFF00DD, 1)),
     ((0, -30), 60, 1.5, (0xFF00DD, 1)),
     ((0, -30), 120, 1.5, (0xFF00DD, 1)),
     ((30, 20), 45, 0.8, (0xFF4400, 1)),
     ((30, 30), 350, 0.8, (0xFF4400, 1)),
     ((-4, -25), 0, 1.5, (0x00FFAA, 1)),
     ((-4, -25), 60, 1.5, (0x00FFAA, 1)),
     ((-4, -25), 120, 1.5, (0x00FFAA, 1)),
    )
    num_portals = [0, 15, len(portals)][playground_level]
    for pos, naut_hdg, radius, styles in portals[:num_portals]:
      mvm.push()
      mvm.translate(pos)
      mvm.rotate_z(np.radians(90 - naut_hdg))
      draw_portal(screen, view, mvm, radius=radius, styles=styles)
      mvm.pop()

    aux = dict()
    if ser is not None:
      aux['reversing'] = (ser_lamps >> 3) & 1;
      aux['stop'] = (ser_lamps >> 2) & 1;
      aux['ldi'] = (ser_lamps >> 1) & 1;
      aux['rdi'] = (ser_lamps >> 0) & 1;
    pv.draw(screen, view, mvm, aux)
    if 0:
      mvm.push()
      mvm.translate(pv.pos[:2])
      mvm.orient(pv.ori)
      #draw_wfo(screen, view, mvm, wfo_sc5k_ref_box)
      draw_wfo(screen, view, mvm, wfo_artcar1_ref_box)
      mvm.pop()

    # Draw the turning circle centre and the lateral acceleration vector.
    turn_c = pv.instr_turn_centre
    trac_c = pv.pos + pv.traction_offset @ pv.ori

    if turn_c is not None:
      ir2 = 0.5 * np.sqrt(2.0)
      points = np.array([
        [0.0, 0.0], [0.0, 0.0],
        [1.0, 0.0], [ir2, ir2], [0.0, 1.0], [-ir2, ir2],
        [-1.0, 0.0], [-ir2, -ir2], [0.0, -1.0], [ir2, -ir2],
      ]) + turn_c[:2].reshape((1, 2))
      points[1] = trac_c[:2]
      points = np.pad(points, ((0, 0), (0, 1)))
      runs = ((0, 1), (3, 7), (5, 9), (2, 3, 4, 5, 6, 7, 8, 9, 2))
      wfo_turn = (
        None,
        points,
        (((0x009900, 1), runs),)
      )
      draw_wfo(screen, view, mvm, wfo_turn)

    draw_flat_vector(
      screen, view, mvm,
      trac_c, trac_c + pv.instr_lat_accel,
      0xFF0000, 2
    )

    draw_flat_vector(
      screen, view, mvm,
      trac_c, trac_c + pv.instr_accel,
      0xCC5500, 2
    )

    knob_col = pg.Color(192, 240, 0)
    margin = int(0.1 * round(joy_surface.get_width()))
    bat_rect = pg.Rect((scr_margin, scr_margin), (16, 40))
    swi_rect.right = joy_rect.right - margin
    swi_rect.bottom = joy_rect.top - gutter
    if ser is None:
      if idm == InputDeviceMode.JOYSTICKS_HPAT:
        # BZT levers
        knob_col = (0, 190, 110)
        lcol = rcol = knob_col
        llev_surface.fill(instr_bg_col)
        draw_lever(llev_surface, bztj_left, True, margin, knob_col=lcol)
        screen.blit(llev_surface, llev_rect)
        rlev_surface.fill(instr_bg_col)
        draw_lever(rlev_surface, bztj_right, True, margin, knob_col=rcol)
        screen.blit(rlev_surface, rlev_rect)
        bat_rect.bottom = llev_rect.bottom
        swi_rect.bottom = llev_rect.bottom - margin
      elif idm == InputDeviceMode.JOYSTICKS_VH:
        # 2-channel RC car-style separate-axes levers
        knob_col = pg.Color(255, 96, 0)
        vlev_surface.fill(instr_bg_col)
        draw_lever(vlev_surface, joystick[1], True, margin,
            knob_col=knob_col)
        screen.blit(vlev_surface, vlev_rect)
        hlev_surface.fill(instr_bg_col)
        draw_lever(hlev_surface, joystick[0], True, margin,
            knob_col=knob_col, horizontal=True)
        screen.blit(hlev_surface, hlev_rect)
        bat_rect.bottom = vlev_rect.top - gutter
        swi_rect.bottom = hlev_rect.top - gutter
      else:
        # Single 2-axis joystick (or mouse)
        joy_surface.fill(instr_bg_col)
        if idm == InputDeviceMode.JOYSTICK_ISO:
          knob_col = pg.Color(240, 0, 0)
          draw_joystick(joy_surface, joystick, margin, knob_col=knob_col)
        else:
          knob_col = pg.Color(240, 0, 180)
          draw_joystick(joy_surface, joystick, margin, knob_col=knob_col,
              mouse=True)
        screen.blit(joy_surface, joy_rect)
        bat_rect.bottom = joy_rect.top - gutter
        swi_rect.bottom = joy_rect.top - gutter

    if ser is None:
      if not limit_turn_rate:
        s = im0i_surface
      else:
        s = im2i_surface if turn_caps.reverse_turns else im1i_surface
      screen.blit(s, imi_rect)

    # Soft controller gauges
    scgauges_surface.fill(instr_bg_col)
    mcol = pg.Color(255, 255, 255)
    ccol = pg.Color(255, 255, 255)
    if motors_are_magic: mcol = knob_col
    if not soften_speed: ccol = knob_col
    inv_max_ws = 1.0 / max_wheel_speed
    #lmtr_defl = lw_ctrl.current_speed * inv_max_ws
    #rmtr_defl = rw_ctrl.current_speed * inv_max_ws
    lmtr_defl = pv.lw_state.linspeed * inv_max_ws
    rmtr_defl = pv.rw_state.linspeed * inv_max_ws
    lcmd_defl = lw_ctrl.target_speed * inv_max_ws
    rcmd_defl = rw_ctrl.target_speed * inv_max_ws
    draw_lr_gauges(
      scgauges_surface,
      (lmtr_defl, rmtr_defl),
      (lcmd_defl, rcmd_defl),
      (mbztj_left, mbztj_right) if ser is None else (None, None),
      (mcol, mcol),
      (ccol, ccol),
      (knob_col, knob_col),
      margin,
    )
    screen.blit(scgauges_surface, scgauges_rect)

    if ser is None:
      # Turn rate gauge
      tr_surface.fill(instr_bg_col)
      mcol = pg.Color(255, 255, 255)
      ccol = pg.Color(255, 255, 255)
      inv_max_omega = 1.0 / max_omega
      tdefl = joystick[0] * max_omega_for_speed * inv_max_omega
      cdefl = soft_joy[0] * max_omega_for_speed * inv_max_omega
      mdefl = -pv.instr_omega * inv_max_omega
      if motors_are_magic:
        mcol = knob_col
      if not soften_turns:
        ccol = knob_col
      im = int(round(margin))
      gh = (tr_rect.size[1] - 2 * im) * 0.75
      igrect = pg.Rect((im, im), (tr_rect.size[0] - 2 * im, gh))
      draw_gauge(
        tr_surface,
        igrect,
        mdefl,
        cdefl,
        tdefl,
        mtr_defl_col=mcol,
        cmd_defl_col=ccol,
        target_col=knob_col,
        signed=True,
        mirrored=False,
        horizontal=True,
      )
      screen.blit(tr_surface, tr_rect)

    if trim != 0.0 or mistrim != 0.0 or trimming or zeroing_trim:
      # Wheel trim gauge
      wt_surface.fill(instr_bg_col)
      k = -1.0 / max_trim
      inv_max_omega = 1.0 / max_omega
      im = int(round(margin))
      gh = (wt_rect.size[1] - 2 * im) * 0.75
      igrect = pg.Rect((im, im), (wt_rect.size[0] - 2 * im, gh))
      if ser is None:
        draw_gauge(
          wt_surface,
          igrect,
          k * (mistrim + trim),
          k * mistrim,
          k * trim,
          signed=True,
          mirrored=True,
          horizontal=True,
        )
      else:
        draw_gauge(
          wt_surface,
          igrect,
          None,
          k * mistrim,
          None,
          signed=True,
          mirrored=True,
          horizontal=True,
        )
      screen.blit(wt_surface, wt_rect)

    if ser is None:
      # Brake gauge
      brake_surface.fill(instr_bg_col)
      defl = speed_ctrl.effective_braking_factor
      ccol = pg.Color(0, 0, 204)
      if speed_ctrl.joy_braking_state != 0:
        ccol = knob_col
      im = int(round(margin))
      gw = (brake_rect.size[0] - 2 * im) * 0.75
      igrect = pg.Rect((im, im), (gw, brake_rect.size[1] - 2 * im))
      draw_gauge(
        brake_surface,
        igrect,
        None,
        None if trimming else defl,
        None,
        mtr_defl_col=knob_col,
        cmd_defl_col=ccol,
        target_col=knob_col,
        signed=False,
        mirrored=True,
        horizontal=False,
      )
      screen.blit(brake_surface, brake_rect)

    if ser is None:
      # Steering wheel indicator
      if turn_caps.reverse_turns:
        effective = limit_turn_rate and idm != InputDeviceMode.JOYSTICKS_HPAT
        swi_surface.set_alpha(instr_icon_alphas[effective])
        screen.blit(swi_surface, swi_rect)

      # Magic motor indicator
      if motors_are_magic:
        screen.blit(mmi_surface, mmi_rect)

      # Joy brake indicator
      if speed_ctrl.enable_joy_brake:
        effective = soften_speed
        jbi_surface.set_alpha(instr_icon_alphas[effective])
        screen.blit(jbi_surface, jbi_rect)

      # Throttle indicator
      if enable_throttle:
        effective = soften_speed
        ti_surface.set_alpha(instr_icon_alphas[effective])
        screen.blit(ti_surface, ti_rect)

    # Flat tyre indicator
    if mistrim != 0.0:
      effective = True
      fti_surface.set_alpha(instr_icon_alphas[effective])
      screen.blit(fti_surface, fti_rect)

    # Battery indicator
    if gamepad is not None:
      if anim_counter & ((1 << 12) - 1) == 0:
        s = gamepad.get_power_level()
        levels = {
          'empty': 0.0,
          'low': 0.25,
          'medium': 0.50,
          'high': 0.75,
          'full': 0.95,
          'max': 1.0,
        }
        gamepad_bat_level = levels.get(s, -1.0)
    if gamepad_bat_level >= 0.0:
      draw_battery(screen, bat_rect, gamepad_bat_level)

    # Numeric displays

    w = screen.get_width()
    std_digit_width = int(round(w * 20.0 / 1280.0))

    # Speedometer (km/h)
    digit_width = 3 * std_digit_width // 2
    digit_height = 2 * digit_width
    cx = 0.5 * w
    x = cx - 4 * 1.6 * digit_width
    speedo_rect = pg.Rect((x, 10), (digit_width, digit_height))
    speed = 3.6 * (0.5 * (pv.lw_state.linspeed + pv.rw_state.linspeed))
    nstr = "{:7.2f}".format(speed)
    draw_nstr_7seg(screen, speedo_rect, 0xFFFFFF, nstr, seg_lw=5,
        small_decimals=True)

    digit_width = std_digit_width // 2
    digit_height = 2 * digit_width

    # Frames per second
    cx = 0.005 * w
    x = cx - 4 * 1.6 * digit_width
    fps_rect = pg.Rect((x, 10), (digit_width, digit_height))
    fps = 1.0 / delta_time
    weight = 0.5
    dampened_fps = dampened_fps + weight * (fps - dampened_fps)
    nstr = "{:7.0f}".format(dampened_fps)
    draw_nstr_7seg(screen, fps_rect, 0x0066FF, nstr, seg_lw=3,
        small_decimals=True)

    digit_width = std_digit_width
    digit_height = 2 * digit_width

    # Turning radius (metres)
    if pv.instr_turn_centre is not None:
      cx = 0.96 * w
      x = cx - 4 * 1.6 * digit_width
      trad_rect = pg.Rect((x, 10), (digit_width, digit_height))
      r = la.norm(pv.instr_turn_centre - trac_c)
      if abs(r) < 999.5:
        nstr = "{:7.2f}".format(r)
        draw_nstr_7seg(screen, trad_rect, 0x00BB00, nstr, seg_lw=4,
            small_decimals=True)

    # Angular speed (degrees per second)
    # Though for right-handed land vehicle coordinates, positive rotation
    # about the up vector corresponds to a left turn, the display is negated
    # to reflect the rate of change of the more familiar nautical heading.
    cx = 0.83 * w
    x = cx - 4 * 1.6 * digit_width
    speedo_rect = pg.Rect((x, 10), (digit_width, digit_height))
    omega_deg = np.degrees(pv.instr_omega)
    if omega_deg != 0.0: omega_deg = -omega_deg
    nstr = "{:7.2f}".format(omega_deg)
    draw_nstr_7seg(screen, speedo_rect, 0x00CCFF, nstr, seg_lw=4,
        small_decimals=True)

    # Lateral acceleration (metres per second per second)
    cx = 0.68 * w
    x = cx - 4 * 1.6 * digit_width
    acc_rect = pg.Rect((x, 10), (digit_width, digit_height))
    a = la.norm(pv.instr_lat_accel)
    nstr = "{:7.2f}".format(a)
    col = 0xFF0000
    seg_lw = 4
    if a > 2.0:
      if ((anim_counter >> 7) & 1):
        col, seg_lw = 0xFF0000, 6
      else:
        col, seg_lw = 0xFFDDDD, 4
    draw_nstr_7seg(screen, acc_rect, col, nstr, seg_lw=seg_lw,
        small_decimals=True)

    # Acceleration (metres per second per second)
    cx = 0.28 * w
    x = cx - 4 * 1.6 * digit_width
    acc_rect = pg.Rect((x, 10), (digit_width, digit_height))
    a = la.norm(pv.instr_accel)
    nstr = "{:7.2f}".format(a)
    col = 0xCC6600
    seg_lw = 4
    if a > 9.81:
      if ((anim_counter >> 7) & 1):
        col, seg_lw = 0xFF6600, 6
      else:
        col, seg_lw = 0xFFEEDD, 4
    draw_nstr_7seg(screen, acc_rect, col, nstr, seg_lw=seg_lw,
        small_decimals=True)

    if joydump and gamepad is not None and not do_exit:
      m = ""
      S = []
      for i in range(gamepad.get_numaxes()):
        a = gamepad.get_axis(i)
        S.append("{:5.2f}".format(a))
      axes = " ".join(S)
      S = []
      for i in range(gamepad.get_numbuttons()):
        b = gamepad.get_button(i)
        S.append((m[i] if i < len(m) else '1') if b else '-')
      buttons = "".join(S)
      S = []
      for i in range(gamepad.get_numhats()):
        h = gamepad.get_hat(i)
        S.append("D-U"[h[1] + 1] + "L-R"[h[0] + 1])
      hats = "".join(S)
      print(axes, buttons, hats)

    pg.display.update()
    #print(len(mvm.stack))

    dt_ms = clock.tick(max_fps)  # Frame rate in Hz
    delta_time = dt_ms / 1000.0
    anim_counter += dt_ms

    turn_ctrl.advance(delta_time)

    speed = 0.5 * (pv.lw_state.linspeed + pv.rw_state.linspeed)
    pv.instr_last_vel = pv.ori[0] * speed

    speed_ctrl.advance(delta_time)
    lw_ctrl.v_pos_ctrl.integral = 0.0
    rw_ctrl.v_pos_ctrl.integral = 0.0
    lw_ctrl.advance(delta_time)
    rw_ctrl.advance(delta_time)
    if motors_are_magic:
      lw_ctrl.current_speed = lw_ctrl.target_speed
      rw_ctrl.current_speed = rw_ctrl.target_speed
    pv.lw_state.ls_integral = lw_trim_factor * lw_ctrl.v_pos_ctrl.integral
    pv.rw_state.ls_integral = rw_trim_factor * rw_ctrl.v_pos_ctrl.integral
    pv.advance(delta_time)
    pv.lw_state.linspeed = lw_trim_factor * lw_ctrl.current_speed
    pv.rw_state.linspeed = rw_trim_factor * rw_ctrl.current_speed
    speed = 0.5 * (pv.lw_state.linspeed + pv.rw_state.linspeed)
    vel = pv.ori[0] * speed
    pv.instr_accel = (vel - pv.instr_last_vel) / delta_time

    # Roughly model the scrubbing stress on the tires.
    twist = 5.0 * pv.instr_omega * delta_time
    f = 15.0
    pv.lw_state.twist += twist
    pv.rw_state.twist += twist
    pv.lw_state.twist *= np.exp(-f * abs(pv.lw_state.linspeed) * delta_time)
    pv.rw_state.twist *= np.exp(-f * abs(pv.rw_state.linspeed) * delta_time)
    pv.lw_state.twist = np.clip(pv.lw_state.twist, -1.0, +1.0)
    pv.rw_state.twist = np.clip(pv.rw_state.twist, -1.0, +1.0)

    if zeroing_trim:
      trim_v = 0.05
      abs_delta_trim = trim_v * delta_time
      if trim > 0.0:
        trim = max(0.0, trim - abs_delta_trim)
      elif trim < 0.0:
        trim = min(0.0, trim + abs_delta_trim)
      if trim == 0.0:
        trim_v = 0.0
    else:
      trim += delta_time * trim_v
      trim = np.clip(trim, -max_trim, +max_trim)

    pv.blinkers.advance(delta_time)

    # Update the (inverted) view distance.
    vd_ctrl.advance(delta_time)

  if ser is not None:
    ser.close();


if __name__ == '__main__':
  main()
  print("Done!")

# TO DO: Switch for actual_speed source
#        Auto blinker cancellation
#        Improve auto-braking speed.
#        Calibration mode
