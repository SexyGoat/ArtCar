#ifndef QPOSCTRL_H_
#define QPOSCTRL_H_


//-----------------------------------------------------------------------------
// Quadratic Position Controller
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
