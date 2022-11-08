import board
import busio
import adafruit_apds9960.apds9960
import time
import paho.mqtt.client as mqtt
import uuid
import signal

import digitalio
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.st7789 as st7789
import urllib, urllib.request, urllib.parse, subprocess

# Configuration for CS and DC pins (these are FeatherWing defaults on M0/M4):
cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = None

# Config for display baudrate (default max is 24mhz):
BAUDRATE = 64000000

backlight = digitalio.DigitalInOut(board.D22)
backlight.switch_to_output()
backlight.value = True
buttonA = digitalio.DigitalInOut(board.D23)
buttonB = digitalio.DigitalInOut(board.D24)
buttonA.switch_to_input()
buttonB.switch_to_input()

# Setup SPI bus using hardware SPI:
spi = board.SPI()

# Create the ST7789 display:
disp = st7789.ST7789(
    spi,
    cs=cs_pin,
    dc=dc_pin,
    rst=reset_pin,
    baudrate=BAUDRATE,
    width=135,
    height=240,
    x_offset=53,
    y_offset=40,
)

# Create blank image for drawing.
# Make sure to create image with mode 'RGB' for full color.
height = disp.width  # we swap height/width to rotate it to landscape!
width = disp.height
image = Image.new("RGB", (width, height))
rotation = 90

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))
disp.image(image, rotation)
# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding
bottom = height - padding


font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)

light_topic = 'IDD/factory1/light'
audio_topic = 'IDD/factory1/audio'
action_topic = 'IDD/factory1/actions'

def google_tts(words):
  url = f"http://translate.google.com/translate_tts?ie=UTF-8&client=tw-ob&q={words}&tl=en"
  subprocess.call(['/usr/bin/mplayer', '-ao', 'alsa', '-really-quiet', '-noconsolecontrols', url])

def on_connect(client, userdata, flags, rc):
    print(f"connected with result code {rc}")
    client.subscribe(light_topic)
    client.subscribe(audio_topic)

last_light_alert = None
last_audio_alert = None
light_msg = f"Light Level: None"
audio_msg = f"Volume Level: None"
light_alert_active = False
audio_alert_active = False

def write_messages(l_msg=light_msg, a_msg=audio_msg, l_active=False, a_active=False):
  if not l_active:
    light_fill = "#0000FF"
  else:
    light_fill = "#FF0000"
  if not a_active:
    audio_fill = "#0000FF"
  else:
    audio_fill = "#FF0000"
  draw.rectangle((0, 0, width, height), outline=0, fill=0)
  x = 0
  y = top
  draw.text((x, y), l_msg, font=font, fill=light_fill)
  disp.image(image, rotation)
  y += font.getsize(l_msg)[1]
  draw.text((x, y), a_msg, font=font, fill=audio_fill)
  disp.image(image, rotation)

write_messages()

def on_message(client, userdata, msg):
  # if a message is recieved on the colors topic, parse it and set the color
  global light_msg, audio_msg, light_alert_active, audio_alert_active, last_light_alert, last_audio_alert, light_topic, audio_topic, action_topic
  print(msg.topic, msg.payload.decode('UTF-8'))
  if msg.topic == light_topic:
    try:
      light_level = int(msg.payload.decode('UTF-8'))
      light_msg = f"Light Level: {light_level}"
      if light_level < 1000 and (last_light_alert == None or time.time() - last_light_alert > 10):
        light_alert_active = True
        # If the threshold was hit and (the last alert was never OR the last alert was more than 10 seconds ago)
        # Speak alert now and change text color to red
        write_messages(light_msg, audio_msg, light_alert_active, audio_alert_active)
        google_tts(f"Alert: Light level in factory 1 has dropped to {light_level}")
        # Also send a message over the broker back so the station knows
        client.publish(action_topic, "Low light level!")
      elif light_level >= 1000:
        light_alert_active = False
        write_messages(light_msg, audio_msg, light_alert_active, audio_alert_active)
    except:
      pass
  elif msg.topic == audio_topic:
    try:
      audio_level = int(msg.payload.decode('UTF-8'))
      audio_msg = f"Volume Level: {audio_level}"
      if audio_level > 85 and (last_audio_alert == None or time.time() - last_audio_alert > 10):
        audio_alert_active = True
        # If the threshold was hit and (the last alert was never OR the last alert was more than 10 seconds ago)
        # Speak alert now and change text color to red
        write_messages(light_msg, audio_msg, light_alert_active, audio_alert_active)
        google_tts(f"Alert: Noise level is high in factory 1")
        # Also send a message over the broker back so the station knows
        client.publish(action_topic, "High noise level!")
      elif audio_level <= 85:
        audio_alert_active = False
        write_messages(light_msg, audio_msg, light_alert_active, audio_alert_active)
    except:
      pass

client = mqtt.Client(str(uuid.uuid1()))
client.tls_set()
client.username_pw_set('idd', 'device@theFarm')
client.on_connect = on_connect
client.on_message = on_message

client.connect(
    'farlab.infosci.cornell.edu',
    port=8883)

client.loop_start()

# this lets us exit gracefully (close the connection to the broker)
def handler(signum, frame):
    print('exit gracefully')
    client.loop_stop()
    exit (0)

# hen sigint happens, do the handler callback function
signal.signal(signal.SIGINT, handler)

while True:
  pass