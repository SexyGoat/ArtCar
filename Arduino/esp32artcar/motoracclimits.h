#ifndef MOTORACCLIMITS_H_
#define MOTORACCLIMITS_H_


//-----------------------------------------------------------------------------
// Motor Acceleration Limits
//-----------------------------------------------------------------------------


class MotorAccLimits {
public:
  float max_fwd_accel;
  float max_fwd_decel;
  float max_rev_accel;
  float max_rev_decel;
  float max_jerk;
  MotorAccLimits(float facc, float fdec, float racc, float rdec, float jerk);
  MotorAccLimits(float accel, float jerk);
  MotorAccLimits();
  void BlendFrom(
    const MotorAccLimits &mal1,
    const MotorAccLimits &mal2,
    float t
  );
};


//-----------------------------------------------------------------------------

#endif  // MOTORACCLIMITS_H_
