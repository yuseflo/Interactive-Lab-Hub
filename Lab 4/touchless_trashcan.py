import time
from adafruit_servokit import ServoKit
import busio
import adafruit_apds9960.apds9960
import board


### SERVO-MOTOR

# Set channels to the number of servo channels on your kit.
# There are 16 channels on the PCA9685 chip.
kit = ServoKit(channels=16)

# Name and set up the servo according to the channel you are using.
servo = kit.servo[2]

# Set the pulse width range of your servo for PWM control of rotating 0-180 degree (min_pulse, max_pulse)
# Each servo might be different, you can normally find this information in the servo datasheet
servo.set_pulse_width_range(500, 2500)

### PROXIMITY

i2c = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_apds9960.apds9960.APDS9960(i2c)
sensor.enable_proximity = True

while True:
    prox = sensor.proximity
    if prox > 3:
        try:
            # Set the servo to 180 degree position
            servo.angle = 90
            time.sleep(4)
            # Set the servo to 0 degree position
            servo.angle = 0

            
        except KeyboardInterrupt:
            # Once interrupted, set the servo back to 0 degree position
            servo.angle = 0
            time.sleep(0.5)
            break