//-----------------------------------------------------------------------------
// Animation (and integration) of Car and General Control State
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

#include "animatecar.h"

#include "inputstate.h"
#include "car.h"
#include "gcstate.h"
#include "blinkers.h"


//-----------------------------------------------------------------------------


void AnimateGCSAndCar(
  GeneralCtrlState& gcs,
  InputState& inp,
  GamepadCal& gpcal,
  Car& car
) {

  CarSpeedCtrl& S = car.speed_ctrl;

  S.enable_joy_brake = gcs.flags.enable_joy_brake;
  car.turn_caps.reverse_turns = gcs.flags.reverse_turns;

  float max_omega_for_speed;
  float max_omega = car.turn_caps.max_turn_rate;
  float max_ctrl_speed = car.max_body_speed;
  if (gcs.idm == kJoystickHPat or gcs.idm == kJoystickModHPat) {
    if (not gcs.flags.limit_turn_rate) {
      max_ctrl_speed = car.max_wheel_speed;
      max_omega = car.max_hpat_omega;
    }
  }
  max_omega_for_speed = max_omega;

  float joystick_x;
  float joystick_y;
  float hpat_left = 0.0f;
  float hpat_right = 0.0f;
  float lefttrigger = JoyAxis2Float(inp.lefttrigger, gpcal.lefttrigger);
  float righttrigger = JoyAxis2Float(inp.righttrigger, gpcal.righttrigger);

  float left_joy_y = -JoyAxis2Float(inp.lefty, gpcal.lefty);
  float right_joy_y = -JoyAxis2Float(inp.righty, gpcal.righty);
  
  // Input layout

  {

    float left_joy_x = JoyAxis2Float(inp.leftx, gpcal.leftx);
    float right_joy_x = JoyAxis2Float(inp.rightx, gpcal.rightx);

    switch (gcs.idm) {

      case kJoystickHPat:
      case kJoystickModHPat:
        {
          float raw_hpat_left = left_joy_y;
          float raw_hpat_right = right_joy_y;
          joystick_x = 0.5f * (raw_hpat_left - raw_hpat_right);
          joystick_y = 0.5f * (raw_hpat_left + raw_hpat_right);
        }
        if (0) {
          if (gcs.flags.limit_turn_rate) {
            float k = car.max_hpat_omega / max_omega;
            joystick_x *= k;
            joystick_x = constrain(joystick_x, -1.0f, +1.0f);
          }
        }
        car.turn_caps.reverse_turns = false;
        break;

      case kJoystickISO:
        joystick_x = left_joy_x;
        joystick_y = left_joy_y;
        break;

      case kJoystickVH:
        joystick_x = right_joy_x;
        joystick_y = left_joy_y;
        break;

      default:
        joystick_x = 0.0f;
        joystick_y = 0.0f;
        break;

    }

  }

  // Trim adjustment

  {
    bool was_trimming = gcs.flags.trimming;
    bool trim_button_pressed = inp.buttons.circle;
    if (trim_button_pressed or gcs.flags.zeroing_trim) {
      gcs.flags.trimming = true;
    }
    if (gcs.flags.trimming) {
      if (gcs.flags.zeroing_trim) {
        if (gcs.trim == 0.0f and gcs.trim_vel == 0.0f) {
          if (lefttrigger == 0.0f and righttrigger == 0.0f) {
            gcs.flags.zeroing_trim = false;
          }
        }
      } else {
        gcs.trim_vel = 0.005f * (lefttrigger - righttrigger);
        if (lefttrigger >= 0.8f and righttrigger >= 0.8f) {
          gcs.flags.zeroing_trim = true;
        }
        if (lefttrigger == 0.0f and righttrigger == 0.0f
            and not trim_button_pressed) {
          gcs.flags.trimming = false;
        }
      }
      lefttrigger = 0.0f;
      righttrigger = 0.0f;
    } else {
      gcs.trim_vel = 0.0f;
    }
  }

  // Jogging

  bool is_jogging = false;
  int8_t jogx = int8_t(inp.buttons.right) - int8_t(inp.buttons.left);
  int8_t jogy = int8_t(inp.buttons.up) - int8_t(inp.buttons.down);
  if (jogx != 0 or jogy != 0) {
    car.turn_caps.reverse_turns = false;
    S.enable_joy_brake = false;
    S.joy_braking_state = 0;
    joystick_x = car.turn_jog_factor * float(jogx);
    joystick_y = car.jog_factor * float(jogy);
    is_jogging = true;
  }

  // Alternative control mode

  if (gcs.flags.use_alt_ctrl_method and not is_jogging) {
    const static float trig_jog_thres = 0.1f;
    const static float inv_cpl_tjt = 1.0f / (1.0f - trig_jog_thres);
    float lt1 = (lefttrigger - trig_jog_thres) * inv_cpl_tjt;
    float rt1 = (righttrigger - trig_jog_thres) * inv_cpl_tjt;
    float t1 = fmaxf(lt1, rt1);
    t1 = constrain(t1, 0.0f, 1.0f);
    if (t1 > 0.0f) {
      joystick_y *= (1.0f - (1.0f - car.jog_factor) * (1.0f - t1));
    }
  }

  // Turn softening

  car.turn_ctrl.target_x = joystick_x;
  if (not gcs.flags.soften_turns) {
    car.turn_ctrl.x = car.turn_ctrl.target_x;
    car.turn_ctrl.v = 0.0f;
  }
  joystick_x = car.turn_ctrl.x;

  // Throttle softening

  S.enable_throttle = gcs.flags.soften_throttle;

  // Speed, ideally sourced from a tachometer

  float actual_speed = S.current_speed;  // <<< Honest, Guv!
  actual_speed =
      0.5f * (car.lw_ctrl.current_speed + car.rw_ctrl.current_speed);

  // Moderated, computed H-pattern control deflections

  float cmd_speed = max_ctrl_speed * joystick_y;

  if (gcs.flags.limit_turn_rate) {
    max_omega_for_speed = car.turn_caps.MaxTurnRateForSpeed(actual_speed);
  }
  float omega = -max_omega_for_speed * joystick_x;
  float half_diff_speed = 0.5f * car.axle_width * omega;

  float inv_max_wheel_speed = 1.0f / car.max_wheel_speed;
  hpat_left = (cmd_speed - half_diff_speed) * inv_max_wheel_speed;
  hpat_right = (cmd_speed + half_diff_speed) * inv_max_wheel_speed;

  hpat_left = constrain(hpat_left, -1.0f, +1.0f);
  hpat_right = constrain(hpat_right, -1.0f, +1.0f);

  // ODDITY: hpat_left and hpat_right not used! <<<<<<<<<

  // Speed control

  float bf = 0.0f;  // Braking factor
  if (not gcs.flags.use_alt_ctrl_method) {
    bf = fmaxf(lefttrigger, righttrigger);
  }
  S.input_braking_factor = bf;
  S.lever_pos = joystick_y;
  S.max_speed = max_ctrl_speed;
  //S.current_speed = actual_speed;  // Causes deadlock.
  S.Animate();
  if (not gcs.flags.soften_speed) {
    S.ForceSpeed(joystick_y * max_ctrl_speed * (1.0f - bf));
  }

  car.lw_ctrl.target_speed = S.current_speed - half_diff_speed;
  car.rw_ctrl.target_speed = S.current_speed + half_diff_speed;

  // Unmoderated H-pattern control
 
  if (gcs.idm == kJoystickHPat) {
    car.lw_ctrl.target_speed = car.max_wheel_speed * left_joy_y;
    car.rw_ctrl.target_speed = car.max_wheel_speed * right_joy_y;
  }
  
  car.lw_ctrl.Animate();
  car.rw_ctrl.Animate();

  gcs.flags.reversing_lamp = actual_speed < -0.001f;

  const float bf_thres = 0.05f;
  float a = S.current_accel;
  if (actual_speed < 0.0f) a = -a;
  if (a < -0.05f or S.joy_braking_state != 0 or bf >= bf_thres) {
    gcs.flags.stop_lamp = true;
  }
  if (a >= -0.01f and S.joy_braking_state == 0 and bf < bf_thres) {
    gcs.flags.stop_lamp = false;
  }

}


//-----------------------------------------------------------------------------


void IntegrateGCSAndCar(
  GeneralCtrlState& gcs,
  Car& car,
  float delta_time
) {

  car.turn_ctrl.Integrate(delta_time);
  car.speed_ctrl.Integrate(delta_time);
  if (gcs.flags.motors_are_magic) {
    car.lw_ctrl.ForceSpeed(car.lw_ctrl.target_speed);
    car.rw_ctrl.ForceSpeed(car.rw_ctrl.target_speed);
  } else {
    car.lw_ctrl.Integrate(delta_time);
    car.rw_ctrl.Integrate(delta_time);
  }

  if (gcs.flags.zeroing_trim) {
    gcs.trim_vel = 0.05f;
    float abs_delta_trim = gcs.trim_vel * delta_time;
    if (gcs.trim > 0.0f) {
      gcs.trim = fmaxf(0.0f, gcs.trim - abs_delta_trim);
    } else if (gcs.trim < 0.0f) {
      gcs.trim = fminf(0.0f, gcs.trim + abs_delta_trim);
    }
    if (gcs.trim == 0.0f) {
      gcs.trim_vel = 0.0f;
    }
  } else {
    gcs.trim += delta_time * gcs.trim_vel;
    gcs.trim = constrain(gcs.trim, -gcs.max_trim, +gcs.max_trim);
  }

}


//-----------------------------------------------------------------------------
