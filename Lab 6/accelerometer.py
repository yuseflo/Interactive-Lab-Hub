import time
import board
import busio
from adafruit_msa3xx import MSA311

import paho.mqtt.client as mqtt
import uuid

client = mqtt.Client(str(uuid.uuid1()))
client.tls_set()
client.username_pw_set('idd', 'device@theFarm')

client.connect(
    'farlab.infosci.cornell.edu',
    port=8883)

topic = 'IDD/your/topic/accelerometer'

i2c = busio.I2C(board.SCL, board.SDA)  # uses board.SCL and board.SDA
msa = MSA311(i2c)

while True:
    val = "%f %f %f" % msa.acceleration
    client.publish(topic, val)
    time.sleep(0.5)
