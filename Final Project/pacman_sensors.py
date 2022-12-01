#!/usr/bin/env python
from samplebase import SampleBase
from runtext import RunText
import adafruit_mpu6050, board, math, time, threading, random
from queue import Queue
from rgbmatrix import graphics
import pyaudio
import numpy as np
from scipy.fft import rfft, rfftfreq
from scipy.signal.windows import hann
from numpy_ringbuffer import RingBuffer
import queue

## Please change the following number so that it matches to the microphone that you are using. 
DEVICE_INDEX = 2

## Compute the audio statistics every `UPDATE_INTERVAL` seconds.
UPDATE_INTERVAL = 0 #1.0

### Things you probably don't need to change
FORMAT=np.float32
SAMPLING_RATE = 44100
CHANNELS=1

def read_pitch_roll(mpu, mpu_queue):
  while True:
    x_accel, y_accel, z_accel = mpu.acceleration
    x_gyro, y_gyro, z_gyro = mpu.gyro
    #print("Acceleration: X:%.2f, Y: %.2f, Z: %.2f m/s^2" % (x_accel, y_accel, z_accel))
    #print("Gyro X:%.2f, Y: %.2f, Z: %.2f rad/s" % (x_gyro, y_gyro, z_gyro))

    accXnorm = x_accel / math.sqrt((x_accel * x_accel) + (y_accel * y_accel) + (z_accel * z_accel))
    accYnorm = y_accel / math.sqrt((x_accel * x_accel) + (y_accel * y_accel) + (z_accel * z_accel))

    pitch = math.asin(accXnorm)
    roll = -math.asin(accYnorm / math.cos(pitch))
      
    pitch = (pitch * 360) / (2*math.pi)
    roll = (roll * 360) / (2*math.pi)

    #print("Pitch {%.2f} Roll {%.2f}" % (pitch, roll))
    # empty out the queue before adding stuff to it, so that when 
    # it is read from elsewhere the latest reading is taken
    with mpu_queue.mutex: 
      mpu_queue.queue.clear()
    mpu_queue.put((pitch, roll))

def read_volume(volume_queue):

  ### Setting up all required software elements: 
  audioQueue = queue.Queue() #In this queue stores the incoming audio data before processing.
  pyaudio_instance = pyaudio.PyAudio() #This is the AudioDriver that connects to the microphone for us.

  def _callback(in_data, frame_count, time_info, status): # This "callbackfunction" stores the incoming audio data in the `audioQueue`
    audioQueue.put(in_data)
    return None, pyaudio.paContinue

  stream = pyaudio_instance.open(input=True,start=False,format=pyaudio.paFloat32,channels=CHANNELS,rate=SAMPLING_RATE,frames_per_buffer=int(SAMPLING_RATE/32),stream_callback=_callback,input_device_index=DEVICE_INDEX)
  
  # One essential way to keep track of variables overtime is with a ringbuffer. 
  # As an example the `AudioBuffer` it stores always the last second of audio data. 
  buffer_time_size = 1 # seconds long buffer.
  AudioBuffer = RingBuffer(capacity=SAMPLING_RATE*buffer_time_size, dtype=FORMAT) 

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

      #print("Volume", volume)
      with volume_queue.mutex: 
        volume_queue.queue.clear()
      volume_queue.put(volume)
      
      nextTimeStamp = UPDATE_INTERVAL+time.time() # See `UPDATE_INTERVAL` above
