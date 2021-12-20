#include "speedctrl.h"

#include "motoracclimits.h"
#include "qposctrl.h"


//-----------------------------------------------------------------------------
// SpeedCtrl methods
//-----------------------------------------------------------------------------


SpeedCtrl::SpeedCtrl(const MotorAccLimits &motor_acc_limits):
  mal {motor_acc_limits},
  _v_pos_ctrl {QPosCtrl(
    motor_acc_limits.max_fwd_accel,
    motor_acc_limits.max_fwd_decel,
    motor_acc_limits.max_jerk,
    0.0f
  )},
  max_speed {0.1f},
  target_speed {0.0f},
  current_speed {0.0f},
  current_accel {0.0f}
{

}


//-----------------------------------------------------------------------------


void SpeedCtrl::ForceSpeed(float v) {
  this->target_speed = v;
  this->current_speed = v;
  this->_v_pos_ctrl.x = v;
  this->_v_pos_ctrl.target_x = v;
  this->_v_pos_ctrl.v = 0.0f;
}


//-----------------------------------------------------------------------------


void SpeedCtrl::Animate() {
  float max_acc;
  float max_dec;
  if (current_speed >= 0.0f) {
    max_acc = this->mal.max_fwd_accel;
    max_dec = this->mal.max_fwd_decel;
  } else {
    max_acc = this->mal.max_rev_decel;
    max_dec = this->mal.max_rev_accel;
  }
  // Using a position controller for velocity control means
  // that the controller's position (x), velocity (v) and
  // acceleration (a) correspond to velocity, acceleration
  // and jerk respectively.
  this->_v_pos_ctrl.max_fwd_v = max_acc;
  this->_v_pos_ctrl.max_rev_v = max_dec;
  this->_v_pos_ctrl.max_a = this->mal.max_jerk;
  this->_v_pos_ctrl.x = this->current_speed;
  this->_v_pos_ctrl.v = this->current_accel;
  this->_v_pos_ctrl.target_x = this->target_speed;
}


//-----------------------------------------------------------------------------


void SpeedCtrl::Integrate(float delta_time) {
  this->_v_pos_ctrl.Integrate(delta_time);
  this->current_speed = this->_v_pos_ctrl.x;
  this->current_accel = this->_v_pos_ctrl.v;
}


//-----------------------------------------------------------------------------
