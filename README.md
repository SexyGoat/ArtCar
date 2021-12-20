#ArtCar

This is an Arduino project for the ESP32-WROOM to send the appropriate
enable and motor speed signals to a pair of frequency inverter to drive
the left and right driving wheels of an electric art car. The input is
supplied from a PS3 Sixaxis controller connected via Bluetooth (and
paired with the help of a Sixaxis pairing tool like WeeSAP).

The ESP32 code translates and moderates the input from the PS3 controller
(which can be H-pattern, ISO or RC car style) and performs speed-dependent
turn rate limiting and acceleration limiting. As no feedback is used,
the motor acceleration limits must be no greater than what the motors
can actually handle.

Include in this project is ArtCarSim, a Pygame-based simulation script,
with a simple wire-frame 3D engine, a couple of car models and a simple
playground to relieve the monotony of the world grid. It is used mainly
to test input control methods and to prototype the car model to be coded
for the ESP32.

The ESP32 code can be made to output serial data to the ArtCarSim Python,
bypassing the Python car modelling and driving the target wheel speeds.
