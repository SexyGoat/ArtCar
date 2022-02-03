//-----------------------------------------------------------------------------
// ArtCar controller prototype for an ESP32
//-----------------------------------------------------------------------------


// ArtCar firmware for ESP32-WROOM
// Version: 0.7.0.0
// (c) Copyright 2022, Daniel Neville


// This program is free software: You can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program. If not, see <https://www.gnu.org/licenses/>.


//-----------------------------------------------------------------------------


// PS3 Controls:
//
// PS: Connect (10s to disconnect)
// Start: Enable motors
// Square: Disable motors
// Select + Square: Reset (and disconnect)
// Select + Circle: Begin joystick and trigger range calibration
// Select + Left: ISO layout (left stick only)
// Select + Up: H-pattern layout (speed and turn rate moderated)
// Select + Right: VH layout (2-channel RC car control)
// Select + Down:: Unmoderated H-pattern layout
// Select + Triangle: Full speed mode ("high gear")
// Select + Cross: Quarter speed mode ("low gear")
// Circle + LeftShoulder: Trim left
// Circle + RightShoulder: Trim right
// Circle + LeftShoulder + RightShoulder: Reset trim
// Triangle: User function 1 (Class 5 Laser)
// DPad (Up, Down, Left, Right) Jog
//
// To do:
//
// Select + LeftShoulder + RightShoulder + LeftStick + RightStick:
//     Unlock PWM calibration mode activation for 3 seconds
// Select + Triangle: Begin PWM calibration mode (if unlocked)
// PWM calibration mode:
//     LeftShoulder/RightShoulder: Enable left/right motor
//     Play: Enable both motors
//     Square: Disable both motors (and apply parking brakes)
//     Up + Joy Up/down: Adjust forward limit
//     Down + Joy Up/down: Adjust reverse limit
//     Left + Joy Up/down: Adjust zero
//     Right + Joy Up/down: Adjust zero (fine)
//     (Joy Left/Right also fine adjust)
//     Cross: Default calibration
//     Circle: Exit and Save calibration
// Serial IO expander


//-----------------------------------------------------------------------------


#include <string.h>
#include <Ps3Controller.h>

#include "qposctrl.h"
#include "turncaps.h"
#include "motoracclimits.h"
#include "speedctrl.h"
#include "carspeedctrl.h"
#include "carmals.h"
#include "car.h"
#include "joycal.h"
#include "joycalnvm.h"
#include "inputstate.h"
#include "gcstate.h"
#include "animatecar.h"
#include "blinkers.h"
#include "btactivity.h"
#include "bitfiddling.h"
#include "virtualio.h"
#include "carsimserial.h"
#include "ps3ledpats.h"


//-----------------------------------------------------------------------------
// Pin assignment
//-----------------------------------------------------------------------------


// Keyes style ESP32-WROOM board (0.8in)
// 
//           Antenna End
//          (3.3V)  (GND)
//             EN    GPIO23
//      IN GPIO36    GPIO22
//      IN GPIO39    TX
//      IN GPIO34    RX
//      IN GPIO35    GPIO21
//         GPIO32    GND
//         GPIO33    GPIO19
//         GPIO25    GPIO18
//         GPIO26    b GPIO5 (WPU)
//         GPIO27    GPIO17
//       GPIO14 n    GPIO16
// (WPD) GPIO12 b    b GPIO4 (WPD)
//            GND|   b GPIO0 BOOT BUTTON (WPU)
//       GPIO13 n|   b GPIO2 (LED) (WPD)
//           D2 f|  nb GPIO15 (WPU) (Pulling down suppresses boot log)
//           D3 f|   f D1
//          CMD f|   f D0
//           5VIN    f CLK
//            MicroUSB End
// 
// Key: f: Flash   b: Boot   n: Noisy (on boot)
//
// "EN" is the 3.3V regulator enable pin. Pulling this to ground
// resets the MCU.
// On many boards, USB-serial wires RTS to EN, DTR to GPIO0:BOOT.
// Internal WPU/WPDs are 45kohms. If switches are to be used, 
// stronger (10kohm) PU/PD resistors should be added.
//
// True GPIO: 16, 17, 18, 19, 21, 22, 23, 25, 26, 27, 32, 33
// GPIO4 is one of the six bootstapping pins, but the corresponding
// bit in the bootstrapping registers is ignored by standard boards.

//18:ME 16:LM 17:RM
//19:JA 32:MA    23:U1 25:BL 27:SL 26:RL 33:BR
//
//LM  RM  ME  JA          U1  BL  RL  SL  MA  BR
//16, 17, 18, 19, 21, 22, 23, 25, 26, 27, 32, 33

enum {
  kVIBitLeftMotorReady,   // GPIO35
  kVIBitRightMotorReady,  // GPIO34
};

enum {
  kVOBitMotorEnableL,   // GPIO18 -> GPIO26
  kVOBitMotorEnableR,   // xxxxxx -> GPIO17
  //kVOBitMotorActivity,  // GPIO32
  kVOBitBluetoothActivity,  // GPIO19 -> GPIO33
  kVOBitUserOut1,       // GPIO23 -> GPIO25
  //kVOBitStopLamp,       // GPIO27
  //kVOBitReversingLamp,  // GPIO26
  //kVOBitLeftBlinker,    // GPIO25
  //kVOBitRightBlinker,   // GPIO33
};

// Be very careful to match Virtual Output enum definitions above with the
// table pin assignment table below to avoid incorrect targetting of pins.

const VOPin vo_pins[] = {
  // Virtual Output pin    GPIO     Sense               Drive and Sink
  {kVOBitMotorEnableL,      26, kVOSenseActiveLow,  kVOutputSinkOnly},
  {kVOBitMotorEnableR,      17, kVOSenseActiveLow,  kVOutputSinkOnly},
  //{kVOBitMotorActivity,     32, kVOSenseActiveLow,  kVOutputSinkOnly},
  {kVOBitBluetoothActivity, 33, kVOSenseActiveLow,  kVOutputSinkOnly},
  {kVOBitUserOut1,          25, kVOSenseActiveLow,  kVOutputSinkOnly},
  //{kVOBitStopLamp,          27, kVOSenseActiveLow,  kVOutputSinkOnly},
  //{kVOBitReversingLamp,     26, kVOSenseActiveLow,  kVOutputSinkOnly},
  //{kVOBitLeftBlinker,       25, kVOSenseActiveLow,  kVOutputSinkOnly},
  //{kVOBitRightBlinker,      33, kVOSenseActiveLow,  kVOutputSinkOnly},
};

const int kNumVOs = sizeof(vo_pins) / sizeof(VOPin);


//-----------------------------------------------------------------------------
// PWM assignment
//-----------------------------------------------------------------------------


const int kLeftMotorPWMCh = 0;
const int kRightMotorPWMCh = 1;
const int kLeftPWMIdle = 2047;
const int kRightPWMIdle = 2047;
const int kLeftPWMGain = 2047 * 90 / 100;
const int kRightPWMGain = 2047 * 90 / 100;

const int kLeftMotorPWMPin = 27;
const int kRightMotorPWMPin = 16;
const int kLeftMotorPWMInverted = true;
const int kRightMotorPWMInverted = true;


//-----------------------------------------------------------------------------
// Main functions
//-----------------------------------------------------------------------------


void InitCar(Car& car, CarMALs& car_mals) {

  car.turn_ctrl = {
    1.0f,  // Max turning stick knob right speed (unsigned)
    1.0f,  // Max turning stick knob left speed (unsigned)
    3.0f,  // Max turning stick knob acceleration (unsigned)
    0.0f,  // Turning stick knob position (in range -1..0..+1)
  };

  {
    TurnCaps& T = car.turn_caps;
    T.max_lat_accel = 2.0f;  // in m/s^2: 1.47m/s^2 std max. for highways.
    T.max_turn_rate = 12.5f * DEG_TO_RAD;  // in rad/s
    T.reversing_omega_slope = 0.4f;  // For stick-to-turn-centre mode
    T.reverse_turns = false;  // Stick-to-turn-centre mode (Set by gcs)
  }

  {
    CarSpeedCtrl& C = car.speed_ctrl;
    C.throttle_factor = 0.08f;
    C.joy_brake_speed_threshold = 0.12f;
    C.enable_joy_brake = 0;  // To be loaded with gcs.flags.enable_joy_brake
  }

  car.jog_factor = 0.18f;
  car.turn_jog_factor = 0.25f;
  car.axle_width = 2.5f;  // m
  car.max_wheel_speed = 5.5f / 3.6f;  // m/s
  car.max_body_speed = 299792458.0f;  // m/s (will be adjusted)
  car.max_hpat_omega = 999.9f;  // rad/s (will be adjusted)

  car.InitComputedValues();

}


//-----------------------------------------------------------------------------


void InitGeneralCtrlState(GeneralCtrlState& gcs) {

  const GeneralCtrlState default_gcs = {
    .idm = kJoystickVH,
    .pwm_scaler = 0.25f,
    .flags = {
      .use_alt_ctrl_method = 0,
      .reverse_turns = 0,
      .limit_turn_rate = 1,
      .enable_joy_brake = 1,
      .soften_speed = 1,
      .soften_turns = 1,
      .soften_throttle = 1,
      .motors_are_magic = 0,
      .trimming = 0,
      .zeroing_trim = 0,
      .stop_lamp = 0,
      .reversing_lamp = 0,
      .enable_motors = 0,
    },
    .max_trim = 0.07f,
    .trim = 0.0f,
    .trim_vel = 0.0f,
  };

  gcs = default_gcs;

}


//-----------------------------------------------------------------------------//-----------------------------------------------------------------------------


void InitInputState(InputState& inp, GamepadCal& gpcal) {

  inp.leftx = JoyAxisMidSlop(gpcal.leftx);
  inp.lefty = JoyAxisMidSlop(gpcal.lefty);
  inp.rightx = JoyAxisMidSlop(gpcal.rightx);
  inp.righty = JoyAxisMidSlop(gpcal.righty);
  inp.lefttrigger = JoyAxisMidSlop(gpcal.lefttrigger);
  inp.righttrigger = JoyAxisMidSlop(gpcal.righttrigger);
  inp.buttons = {};

}


//-----------------------------------------------------------------------------
// Variables
//-----------------------------------------------------------------------------


uint32_t vo_states = 0;

uint32_t last_us_count;
uint32_t last_ms_count;
int blink_timer = 0;

// For a car with a max speed of 6.5km/h (1.8056m/s) at 50Hz, multiply
// the m/s and m/s/s figures here by 27.6923 to get the Hz and Hz/s figures.

CarMALs car_mals = {
  // The wheel acceleration limits are in terms of the linear speed
  // of the centre of the hub relative to the ground or road surface.
  // All parameters should be strictly positive.
  .wheel_mal = {
    1.50f,  // Forward acceleration in m/s^2
    1.50f,  // Forward deceleration in m/s^2
    1.50f,  // Reverse acceleration in m/s^2
    1.50f,  // Reverse deceleration in m/s^2
    9.00f,  // Jerk in m/s^3
  },
  // The normal or "cruise" acceleration limits should be less than
  // the wheel acceleration limits to ensure that the motors are able
  // to catch up to commanded speeds.
  .cruise_mal = {
    0.80f,  // Forward acceleration in m/s^2
    1.00f,  // Forward deceleration in m/s^2
    0.80f,  // Reverse acceleration in m/s^2
    1.00f,  // Reverse deceleration in m/s^2
    4.00f,  // Jerk in m/s^3
  },
  // The braking acceleration limits should be less than the wheel
  // acceleration limits if the motors do all the braking. If real
  // proportional brakes are used, higher decelerations are possible,
  .braking_mal = {
    0.80f,  // Fowrard acceleration in m/s^2
    1.40f,  // Forward deceleration in m/s^2
    0.80f,  // Reverse acceleration in m/s^2
    1.40f,  // Reverse deceleration in m/s^2
    8.00f,  // Jerk in m/s^3
  }
};

Car car {car_mals.wheel_mal, car_mals.cruise_mal, car_mals.braking_mal};
GeneralCtrlState gcs;
GamepadCal gpcal;
InputState input_state;
Blinkers blinkers;
int8_t prev_joy_braking_state = false;
BTActivity bt_activity;

int16_t display_countdown = 0;
int8_t display_state = kLEDPatDispIx_Batt;
bool display_hold = true;

GamepadCalState gp_cal_proc_state;
bool calibrating_joysticks = false;
bool reset_trigger = false;
uint8_t gamepad_mac48[6];
int gpcal_slot_index = -1;
JoyCalKeeper gpcal_keeper;


//-----------------------------------------------------------------------------


void SystemReset() {
  
  ledcWrite(kLeftMotorPWMCh, kLeftPWMIdle);
  ledcWrite(kRightMotorPWMCh, kRightPWMIdle);
  vo_states = 0;
  WritePins(vo_states, vo_pins, kNumVOs);
  ESP.restart();
      
}


//-----------------------------------------------------------------------------


void OnGamepadConnect(){
  
  if (Ps3.isConnected()) {
    
    Serial.println(F("=== Connected ==="));
    String macstr = Ps3.getAddress();
    Serial.print(F("Gamepad MAC: "));
    Serial.println(macstr);
    
    sscanf(
      &macstr[0],
      "%hhx:%hhx:%hhx:%hhx:%hhx:%hhx",
      &gamepad_mac48[0], &gamepad_mac48[1], &gamepad_mac48[2],
      &gamepad_mac48[3], &gamepad_mac48[4], &gamepad_mac48[5]
    );
    gpcal_slot_index = gpcal_keeper.FindSlotByMAC(gamepad_mac48);
    
    if (gpcal_slot_index >= 0) {
      JoyNMVSlot fetched_slot;
      gpcal_keeper.LoadSlot(gpcal_slot_index, fetched_slot);
      gpcal = fetched_slot.gamepad_cal;
      Serial.print(F("Loaded gamepad calibration from Slot "));
      Serial.print(gpcal_slot_index);
      Serial.println(F("."));
    } else {
      Serial.println(F("No calibration record found for this gamepad."));
    }
    
    Ps3.setRumble(100.0f, 100); // Oddly not having any effect.
    display_countdown = 30;
    
  } else {
    
    Serial.println(F("=== Disconnection notice via Connection callback! ==="));
    
  }
  
}


//-----------------------------------------------------------------------------


void OnGamepadDisconnect(){
  // Oddly, never called.
  Serial.println(F("=== Disconnected ==="));
}


//-----------------------------------------------------------------------------


void OnGamepadEvent()
{

  const int gear_high = 1.0f;
  const int gear_low = 0.25f;

  if (Ps3.event.analog_changed.stick.lx
    or Ps3.event.analog_changed.stick.ly
    or Ps3.event.analog_changed.stick.rx
    or Ps3.event.analog_changed.stick.ry
    or Ps3.event.analog_changed.button.up
    or Ps3.event.analog_changed.button.down
    or Ps3.event.analog_changed.button.left
    or Ps3.event.analog_changed.button.right
    or Ps3.event.analog_changed.button.l1
    or Ps3.event.analog_changed.button.r1
    or Ps3.event.analog_changed.button.l2
    or Ps3.event.analog_changed.button.r2
    or Ps3.event.analog_changed.button.cross
    or Ps3.event.analog_changed.button.circle
    or Ps3.event.analog_changed.button.triangle
    or Ps3.event.analog_changed.button.square
    or Ps3.event.button_down.l3
    or Ps3.event.button_down.r3
    or Ps3.event.button_down.select
    or Ps3.event.button_down.start
    or Ps3.event.button_down.ps
    or Ps3.event.button_up.l3
    or Ps3.event.button_up.r3
    or Ps3.event.button_up.select
    or Ps3.event.button_up.start
    or Ps3.event.button_up.ps
  ) {
    bt_activity.activity_ms = 15;
  }
  
  if (Ps3.event.button_down.start) {
    if (not calibrating_joysticks) {
      if (not gcs.flags.enable_motors) {
        Ps3.setRumble(80.0f, 50);
        display_countdown = 50;
      }
      gcs.flags.enable_motors = true;
    }
  }
  if (Ps3.event.button_down.square) {
    if (Ps3.data.button.select) {
      // Begin system reset
      Serial.println(F("Resetting..."));
      display_state = 0;
      display_countdown = 70;
        Ps3.setRumble(100.0f, 70);
      gcs.flags.enable_motors = false;
      reset_trigger = true;
    } else {
      if (not calibrating_joysticks) {
        if (gcs.flags.enable_motors) {
          Ps3.setRumble(80.0f, 35);
          display_countdown = 35;
        }
        gcs.flags.enable_motors = false;
      }
    }
  }

  if (not calibrating_joysticks) {
    if (Ps3.event.button_down.left) {
      if (Ps3.data.button.select) {
        gcs.flags.enable_joy_brake = true;
        gcs.flags.use_alt_ctrl_method = false;
        display_state = kLEDPatDispIx_Layout;
        display_countdown = 30;
        display_hold = true;
        if (gcs.idm != kJoystickISO) Ps3.setRumble(75.0f, 30);
        gcs.idm = kJoystickISO;
      }
    }
    if (Ps3.event.button_down.up) {
      if (Ps3.data.button.select) {
        gcs.flags.enable_joy_brake = false;
        gcs.flags.use_alt_ctrl_method = false;
        display_state = kLEDPatDispIx_Layout;
        display_countdown = 30;
        display_hold = true;
        if (gcs.idm != kJoystickModHPat) Ps3.setRumble(75.0f, 30);
        gcs.idm = kJoystickModHPat;
      }
    }
    if (Ps3.event.button_down.right) {
      if (Ps3.data.button.select) {
        gcs.flags.enable_joy_brake = true;
        gcs.flags.use_alt_ctrl_method = false;
        display_state = kLEDPatDispIx_Layout;
        display_countdown = 30;
        display_hold = true;
        if (gcs.idm != kJoystickVH) Ps3.setRumble(75.0f, 30);
        gcs.idm = kJoystickVH;
      }
    }
    if (Ps3.event.button_down.down) {
      if (Ps3.data.button.select) {
        gcs.flags.enable_joy_brake = false;
        gcs.flags.use_alt_ctrl_method = false;
        display_state = kLEDPatDispIx_Layout;
        display_countdown = 30;
        display_hold = true;
        if (gcs.idm != kJoystickHPat) Ps3.setRumble(75.0f, 30);
        gcs.idm = kJoystickHPat;
      }
    }
  }

  if (not calibrating_joysticks) {
    if (Ps3.event.button_down.triangle) {
      if (Ps3.data.button.select) {
        // Select high gear.
        display_state = kLEDPatDispIx_Speed;
        display_countdown = 30;
        display_hold = true;
        if (gcs.pwm_scaler != gear_high) Ps3.setRumble(90.0f, 30);
        gcs.pwm_scaler = gear_high;
      } else {
        // Fire the laser!
        Ps3.setRumble(75.0f, 22);
      }
    }
    if (Ps3.event.button_down.cross) {
      if (Ps3.data.button.select) {
        // Select low gear.
        display_state = kLEDPatDispIx_Speed;
        display_countdown = 30;
        display_hold = true;
        if (gcs.pwm_scaler != gear_low) Ps3.setRumble(90.0f, 30);
        gcs.pwm_scaler = gear_low;
      }
    }
    if (Ps3.event.button_down.circle) {
      if (Ps3.data.button.select) {
        // Enter joystick calibration mode.
        gcs.flags.enable_motors = false;
        calibrating_joysticks = true;
        gp_cal_proc_state = {};
        display_state = 4;
        display_countdown = 40;
        display_hold = true;
        Ps3.setRumble(80.0f, 100);
      }
    }
  }

  if (calibrating_joysticks) {
    gcs.flags.enable_motors = false;
    if (display_state < 4) {
      if (Ps3.event.button_down.triangle) {
        // Violently shake controller to assist slop calibration.
        Ps3.setRumble(100.0f, 500);
        display_countdown = 200;
      }
      if (Ps3.event.button_down.circle) {
        // Exit gaepad calirbation mode and save calibration.
        calibrating_joysticks = false;
        display_countdown = 40;
        display_state = kLEDPatDispIx_Batt;
        display_hold = true;
        Ps3.setRumble(80.0f, 100);
        JoyNMVSlot gpcal_slot;
        memcpy(gpcal_slot.mac48, gamepad_mac48, 6);
        gpcal_slot.gamepad_cal = gpcal;
        gpcal_slot_index = gpcal_keeper.SaveSlot(gpcal_slot_index, gpcal_slot);
        Serial.print(F("Saved gamepad calibration to Slot "));
        Serial.print(gpcal_slot_index);
        Serial.println(F("."));
      }
    }
  }

}


//-----------------------------------------------------------------------------
// Arduino Main functions
//-----------------------------------------------------------------------------


void setup() {
  
  const char* mac_str = "47:4f:41:54:53:45";  // "GOATSE"
  
  // Choose a moderate PWM frequency. Optocoupler smearing was rather
  // pronounced at 5kHz.
  //
  // For motor speed controllers with adjustable PWM width thresholds,
  // Restrict the range of PWM modulation/ so that the rising and
  // falling edges are always separated by definite periods of steady
  // high and steady low levels. That will ensure linearity.
  const int pwm_freq = 1000;  // Hz

  // For 5kHz, 13 bits is the maximum precision available.
  const int pwm_num_bits = 12;

  InitCar(car, car_mals);
  prev_joy_braking_state = false;
  InitGeneralCtrlState(gcs);
  InitGamepadCalibration(gpcal);
  InitInputState(input_state, gpcal);

  last_us_count = micros();
  last_ms_count = millis();
  delay(10);
  Serial.begin(115200);
  delay(10);
  ConfigPins(vo_states, vo_pins, kNumVOs);
  
  ledcAttachPin(kLeftMotorPWMPin, kLeftMotorPWMCh);
  ledcAttachPin(kRightMotorPWMPin, kRightMotorPWMCh);
  ledcSetup(kLeftMotorPWMCh, pwm_freq, pwm_num_bits);
  ledcSetup(kRightMotorPWMCh, pwm_freq, pwm_num_bits);
  ledcWrite(kLeftMotorPWMCh, kLeftPWMIdle);
  ledcWrite(kRightMotorPWMCh, kRightPWMIdle);
  GPIO.func_out_sel_cfg[kLeftMotorPWMPin].inv_sel = kLeftMotorPWMInverted;
  GPIO.func_out_sel_cfg[kRightMotorPWMPin].inv_sel = kRightMotorPWMInverted;

  Ps3.attach(OnGamepadEvent);
  Ps3.attachOnConnect(OnGamepadConnect);
  Ps3.attachOnDisconnect(OnGamepadDisconnect);
  Serial.println();
  Serial.print(F("Host MAC: "));
  Serial.println(mac_str);
  Ps3.begin(mac_str);

  bt_activity.state = 1;
  
}


//-----------------------------------------------------------------------------


void loop() {
  
  static float cum_time;
  static int iter_count;
  char acs_state_buf[9];

  // Determine the delta time. It turns out that the Arduino milliseconds
  // counter and the microseconds counter each independently count and
  // overflow in binary so that after about 71 minutes, millis() will no
  // longer return a value that is about 1000th of what micros() returns.
  //
  // Though millisecond update intervals are more than adequate for this
  // application, it is nice to measure delta time to microsecond precision.
  // For this reason, the determination of delta time in microseconds (us)
  // is performed inside the code block executed in the case of a non-zero
  // millisecond delta time.
  //
  // The typecasts to (signed) integers are to make the delta time values
  // easy to use with general signed arithmetic.

  uint32_t new_ms_count = millis();
  int32_t delta_ms = (int32_t) (new_ms_count - last_ms_count) & 0x7FFF;
  last_ms_count = new_ms_count;

  if (delta_ms) {
    // A definite time has passed.

    uint32_t new_us_count = micros();
    int32_t delta_us = (int32_t) (new_us_count - last_us_count) & 0x7FFFFFFF;
    last_us_count = new_us_count;
    float delta_time = float(delta_us) * 1e-6f;

    if (Ps3.isConnected()) {
      bt_activity.state = 2;
    } else {
      if (bt_activity.state == 2) {
        bt_activity.state = 0;
        InitInputState(input_state, gpcal);
      }
      gcs.flags.enable_motors = false;
    }

    if (true or gcs.flags.enable_motors) {
      input_state.leftx = uint8_t(int16_t(Ps3.data.analog.stick.lx) + 128);
      input_state.lefty = uint8_t(int16_t(Ps3.data.analog.stick.ly) + 128);
      input_state.rightx = uint8_t(int16_t(Ps3.data.analog.stick.rx) + 128);
      input_state.righty = uint8_t(int16_t(Ps3.data.analog.stick.ry) + 128);
      input_state.lefttrigger = Ps3.data.analog.button.l2;
      input_state.righttrigger = Ps3.data.analog.button.r2;
      input_state.buttons = Ps3.data.button;
    }

    AnimateGCSAndCar(gcs, input_state, gpcal, car);
    blinkers.input = 0;
    blinkers.input = (input_state.buttons.l1 << 1)
                     + (input_state.buttons.r1 << 0);
    blinkers.Animate();

    IntegrateGCSAndCar(gcs, car, delta_time);
    blinkers.Integrate_ms(delta_ms);

    {
      int lm_ocr;
      int rm_ocr;
      float lsf;
      float rsf;
      float lw_trim_factor;
      float rw_trim_factor;
      {
        float x;
        x = 1.0f + gcs.trim;
        lw_trim_factor = constrain(x, 0.0f, 1.0f);
        x = 1.0f - gcs.trim;
        rw_trim_factor = constrain(x, 0.0f, 1.0f);
      }
      
      if (true or gcs.flags.enable_motors) {
        float f = gcs.pwm_scaler / car.max_wheel_speed;
        lsf = car.lw_ctrl.target_speed * lw_trim_factor * f;
        rsf = car.rw_ctrl.target_speed * rw_trim_factor * f;
      } else {
        lsf = rsf = 0.0;
      }
      lm_ocr = round(kLeftPWMIdle + kLeftPWMGain * lsf);
      rm_ocr = round(kRightPWMIdle + kRightPWMGain * rsf);
      lm_ocr = constrain(lm_ocr,
          kLeftPWMIdle - kLeftPWMGain, kLeftPWMIdle + kLeftPWMGain);
      rm_ocr = constrain(rm_ocr,
          kRightPWMIdle - kRightPWMGain, kRightPWMIdle + kRightPWMGain);
  
      ledcWrite(kLeftMotorPWMCh, lm_ocr);
      ledcWrite(kRightMotorPWMCh, rm_ocr);
      
    }

    const float moving_threshold = 0.001f;
    bool lw_moving = fabsf(car.lw_ctrl.current_speed) > moving_threshold;
    bool rw_moving = fabsf(car.rw_ctrl.current_speed) > moving_threshold;
    bool btc = bt_activity.state == 2;
    vo_states = WriteBit(vo_states, kVOBitMotorEnableL,
        gcs.flags.enable_motors);
    vo_states = WriteBit(vo_states, kVOBitMotorEnableR,
        gcs.flags.enable_motors);
    vo_states = WriteBit(vo_states, kVOBitBluetoothActivity,
        bt_activity.lamp_state);
    //vo_states = WriteBit(vo_states, kVOBitMotorActivity,
    //    btc and (lw_moving or rw_moving));
    vo_states = WriteBit(vo_states, kVOBitUserOut1,
        btc and input_state.buttons.triangle);
    //vo_states = WriteBit(vo_states, kVOBitReversingLamp,
    //    btc and gcs.flags.reversing_lamp);
    //vo_states = WriteBit(vo_states, kVOBitStopLamp,
    //    btc and gcs.flags.stop_lamp);
    //vo_states = WriteBit(vo_states, kVOBitLeftBlinker,
    //    btc and ((blinkers.state >> 1) & 1)
    //    and (blinkers.phase < blinkers.on_period));
    //vo_states = WriteBit(vo_states, kVOBitRightBlinker,
    //    btc and ((blinkers.state >> 0) & 1) 
    //    and (blinkers.phase < blinkers.on_period));

    if (0) {
      if (Ps3.isConnected()) {
        if (prev_joy_braking_state != car.speed_ctrl.joy_braking_state) {
          if (prev_joy_braking_state == 0) {
            Ps3.setRumble(100.0f, 40);
          } else {
            Ps3.setRumble(80.0f, 30);
          }
        }
      }
    }
  
    bt_activity.Animate();
    bt_activity.Integrate_ms(delta_ms);
    WritePins(vo_states, vo_pins, kNumVOs);
  
    if (Ps3.isConnected() and not calibrating_joysticks and not reset_trigger) {
      
      const float cum_period = 0.2f;
      cum_time += delta_time;
      ++iter_count;
  
      //delay(50); // <<<<<<<<<<<< Testing
      if (cum_time >= cum_period) {
  
        float freq = float(iter_count) / cum_period;
  
        if (0) {
          SetArtCarSimStateStr(acs_state_buf, input_state, car, gcs, blinkers);
          Serial.println(acs_state_buf);
        }
  
        if (0) {
          float ts = -JoyAxis2Float(input_state.lefty, gpcal.lefty)
              * car.max_body_speed;
          Serial.print(ts); Serial.print(" ");
          //Serial.print(car.turn_ctrl.x); Serial.print(" ");
          Serial.print(car.speed_ctrl.target_speed); Serial.print(" ");
          Serial.print(car.speed_ctrl.current_speed); Serial.print(" ");
          Serial.print(car.lw_ctrl.current_speed); Serial.print(" ");
          Serial.print(car.rw_ctrl.current_speed); Serial.print(" ");
          Serial.println();
        }

        if (0) {
          float x0 = float(input_state.leftx - 128) / 128.0f;
          float x1 = JoyAxis2Float(input_state.leftx, gpcal.leftx);
          Serial.print(x0); Serial.print(" ");
          Serial.print(x1); Serial.print(" ");
          Serial.println();
        }
        
        cum_time -= cum_period;
        iter_count = 0;
      }
      
      prev_joy_braking_state = car.speed_ctrl.joy_braking_state;
  
      display_countdown -= delta_ms;
      
      if (display_countdown <= 0) {
  
        display_countdown += kLEDPatMilliseconds;
        if (not display_hold) {
          display_state += 1;
        }
        if (display_state >= kLEDPatDispIx_NumItems) {
          display_state = 0;
        }
        display_hold = false;
  
        int playernum;
        
        switch (display_state) {
          
          case kLEDPatDispIx_Batt:
            switch (Ps3.data.status.battery) {
              case ps3_status_battery_full:
                playernum = kLEDPat_BattLevel4;
                break;
              case ps3_status_battery_high:
                playernum = kLEDPat_BattLevel3;
                break;
              case ps3_status_battery_low:  
                playernum = kLEDPat_BattLevel2;
                break;
              case ps3_status_battery_dying:
                playernum = kLEDPat_BattLevel1;
                break;
              case ps3_status_battery_shutdown:
                playernum = kLEDPat_BattLevel1;
                break;
              case ps3_status_battery_charging:
                playernum = 0;
                break;
              default:
                playernum = 0;
                break;
            }
            if (!playernum) {
              playernum = 10;
            }
            Ps3.setPlayer(playernum);
            break;
            
          case kLEDPatDispIx_Layout:
            switch (gcs.idm) {
              case kJoystickVH:       playernum = kLEDPat_JoyVH; break;
              case kJoystickISO:      playernum = kLEDPat_JoyISO; break;
              case kJoystickHPat:     playernum = kLEDPat_JoyHPat; break;
              case kJoystickModHPat:  playernum = kLEDPat_JoyModHPat; break;
              default: playernum = 0; break;
            }
            if (playernum) {
              Ps3.setPlayer(playernum);
            }
            break;
            
          case kLEDPatDispIx_Speed:
            if (gcs.pwm_scaler < 0.95f) {
              Ps3.setPlayer(kLEDPat_Slow);
            } else {
              Ps3.setPlayer(kLEDPat_Fast);
            }
            break;
            
          default:
            break;
            
        }
        
      }
      
    }
    
    if (Ps3.isConnected() and calibrating_joysticks and not reset_trigger) {

      CalibrateGamepad(
        gpcal,
        input_state,
        gp_cal_proc_state,
        delta_ms
      );

      display_countdown -= delta_ms;
      if (display_countdown <= 0) {
        display_countdown += 100;
        if (not display_hold) {
          display_state = (display_state + 1) & 3;
        }
        display_hold = false;  
        Ps3.setPlayer((display_state & 3) + 1);
      }
      
    }

    if (reset_trigger) {

      display_countdown -= delta_ms;
      if (display_countdown <= 0) {
        display_countdown += 100;
        display_state = (display_state + 1) & 31;
        display_hold = false;
        if (Ps3.isConnected()) {
          if (display_state < 10) {  
            Ps3.setPlayer((display_state & 1) ? 1 : 4);
          } else {
            Ps3.setPlayer(10);
          }
        }
      }

      if (display_state > 10) {
        if (Ps3.isConnected()) {
          Ps3.end();
        }
        if (display_state > 13) {
          SystemReset();
        }
      }
      
    }
    
  } // A definite time has passed.
  
}
