import pyaudio
import numpy as np
from scipy.fft import rfft, rfftfreq
from scipy.signal.windows import hann
from numpy_ringbuffer import RingBuffer

from threading import Thread

import queue
import time

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


##### LIGHT #####


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

i2c = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_apds9960.apds9960.APDS9960(i2c)

sensor.enable_color = True
r, g, b, a = sensor.color_data

topic_light = 'IDD/factory1/light'
topic_audio = 'IDD/factory1/audio'
topic_actions = 'IDD/factory1/actions'

def on_connect(client, userdata, flags, rc):
    print(f"connected with result code {rc}")
    client.subscribe(topic_actions)

font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)


def google_tts(words):
  url = f"http://translate.google.com/translate_tts?ie=UTF-8&client=tw-ob&q={words}&tl=en"
  subprocess.call(['/usr/bin/mplayer', '-ao', 'alsa', '-really-quiet', '-noconsolecontrols', url])



def on_message(client, userdata, msg):
    rotation = 90
    # if a message is recieved on the colors topic, parse it and set the color
    if msg.topic == topic_actions:
        draw.rectangle((0, 0, width, height*0.5), fill="#000000")
        draw.text((40,30), msg.payload.decode('UTF-8'), font=font, fill="#FF0000")

        google_tts(msg.payload.decode('UTF-8'))
        disp.image(image, rotation)


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

##### AUDIO #####

## Please change the following number so that it matches to the microphone that you are using. 
DEVICE_INDEX = 2

## Compute the audio statistics every `UPDATE_INTERVAL` seconds.
UPDATE_INTERVAL = 5.0



### Things you probably don't need to change
FORMAT=np.float32
SAMPLING_RATE = 44100
CHANNELS=1



# our main loop
def audio_streaming():
        # LIGHT
        
        # AUDIO

        audioQueue = queue.Queue() #In this queue stores the incoming audio data before processing.
        pyaudio_instance = pyaudio.PyAudio() #This is the AudioDriver that connects to the microphone for us.

        def _callback(in_data, frame_count, time_info, status): # This "callbackfunction" stores the incoming audio data in the `audioQueue`
            audioQueue.put(in_data)
            return None, pyaudio.paContinue

        stream = pyaudio_instance.open(input=True,start=False,format=pyaudio.paFloat32,channels=CHANNELS,rate=SAMPLING_RATE,frames_per_buffer=int(SAMPLING_RATE/2),stream_callback=_callback,input_device_index=DEVICE_INDEX)
        

        # One essential way to keep track of variables overtime is with a ringbuffer. 
        # As an example the `AudioBuffer` it stores always the last second of audio data. 
        AudioBuffer = RingBuffer(capacity=SAMPLING_RATE*1, dtype=FORMAT) # 1 second long buffer.
        
        # Another example is the `VolumeHistory` ringbuffer. 
        VolumeHistory = RingBuffer(capacity=int(20/UPDATE_INTERVAL), dtype=FORMAT) ## This is how you can compute a history to record changes over time
        ### Here  is a good spot to extend other buffers  aswell that keeps track of varailbes over a certain period of time. 

        nextTimeStamp = time.time()
        stream.start_stream()
        while True:

            frames = audioQueue.get() #Get DataFrom the audioDriver (see _callbackfunction how the data arrives)
            if not frames:
                continue

            framesData = np.frombuffer(frames, dtype=FORMAT) 
            AudioBuffer.extend(framesData[0::CHANNELS]) #Pick one audio channel and fill the ringbuffer. 
                    
            if(AudioBuffer.is_full and  # Waiting for the ringbuffer to be full at the beginning.
                audioQueue.qsize()<2 and # Make sure there is not alot more new data that should be used. 
                time.time()>nextTimeStamp): # See `UPDATE_INTERVAL` above.

                        buffer  = np.array(AudioBuffer) #Get the last second of audio. 
                        volume = np.rint(np.sqrt(np.mean(buffer**2))*10000) # Compute the rms volume
                        VolumeHistory.append(volume)
                        
                        ## Computes the Frequency Foruier analysis on the Audio Signal.
                        N = buffer.shape[0] 
                        window = hann(N) 
                        amplitudes = np.abs(rfft(buffer*window))[25:] #Contains the volume for the different frequency bin.
                        frequencies = (rfftfreq(N, 1/SAMPLING_RATE)[:N//2])[25:] #Contains the Hz frequency values. for the different frequency bin.


                        LoudestFrequency = frequencies[amplitudes.argmax()]
                        
                        print("Volume:",volume)

                        client.publish(topic_audio, int(volume))
            
                        
                        nextTimeStamp = UPDATE_INTERVAL+time.time() 


        disp.image(image)
        time.sleep(.01)

def light_streaming():
    while True:
        r, g, b, a = sensor.color_data

        # if we press the button, send msg to change everyones color
        client.publish(topic_light, f"{a}")
        time.sleep(5)

if __name__ == '__main__':
    Thread(target = audio_streaming).start()
    Thread(target = light_streaming).start()



