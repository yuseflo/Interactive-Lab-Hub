# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import time
import board
import adafruit_mpu6050
import math

i2c = board.I2C()  # uses board.SCL and board.SDA
mpu = adafruit_mpu6050.MPU6050(i2c)

while True:
    x_accel, y_accel, z_accel = mpu.acceleration
    x_gyro, y_gyro, z_gyro = mpu.gyro
    #print("Acceleration: X:%.2f, Y: %.2f, Z: %.2f m/s^2" % (x_accel, y_accel, z_accel))
    #print("Gyro X:%.2f, Y: %.2f, Z: %.2f rad/s" % (x_gyro, y_gyro, z_gyro))

    accXnorm = x_accel / math.sqrt((x_accel * x_accel) + (y_accel * y_accel) + (z_accel * z_accel))
    accYnorm = y_accel / math.sqrt((x_accel * x_accel) + (y_accel * y_accel) + (z_accel * z_accel))

    pitch = math.asin(accXnorm)
    roll = -math.asin(accYnorm / math.cos(pitch))

    # TODO convert pitch, roll back to degrees for easier debugging
    # TODO gimbal lock issue with 90 deg for pitch which is a problem since cos(90)=0
    pitch = (pitch * 360) / (2*math.pi)
    roll = (roll * 360) / (2*math.pi)

    print("Pitch {%.2f} Roll {%.2f}" % (pitch, roll))

    #print("Temperature: %.2f C" % mpu.temperature)
    print("")
    time.sleep(0.5)