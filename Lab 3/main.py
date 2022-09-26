#!/usr/bin/env python3

from vosk import Model, KaldiRecognizer
import sys
import os
import wave

if not os.path.exists("model"):
    print ("Please download the model from https:/cd/github.com/alphacep/vosk-api/blob/master/doc/models.md and unpack as 'model' in the current folder.")
    exit (1)

wf = wave.open(sys.argv[1], "rb")
if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
    print ("Audio file must be WAV format mono PCM.")
    exit (1)


model = Model("model")
rec = KaldiRecognizer(model, wf.getframerate(), '["one two three four five zero"]')

while True:
    data = wf.readframes(4000)
    if len(data) == 0:
        break
    if rec.AcceptWaveform(data):
        print(rec.Result())
    else:
        print(rec.PartialResult())

print(rec.FinalResult())

# def speak(line):
#     cmd = "./speak.sh \"{}\"".format(line)
#     os.system(cmd)

# # main game loop
# speak("What do you need today")
# input("I want to know how the weather is today")
# speak("For which location should I check?")
# #speak("Swipe the sensor to purchase a share")
