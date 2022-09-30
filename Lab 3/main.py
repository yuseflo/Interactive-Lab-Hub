#!/usr/bin/env python3

from vosk import Model, KaldiRecognizer
import sys
import os
import wave
import board
import busio
import adafruit_apds9960.apds9960
import time

def text2speech():

    if not os.path.exists("model"):
        print ("Please download the model from https:/cd/github.com/alphacep/vosk-api/blob/master/doc/models.md and unpack as 'model' in the current folder.")
        exit (1)

    wf = wave.open(sys.argv[1], "rb")
    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
        print ("Audio file must be WAV format mono PCM.")
        exit (1)

    model = Model("model")
    rec = KaldiRecognizer(model, wf.getframerate(), '["history occupation surgery heart valve biological artifical \
    employee nurse past surgeries available "]')

    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            print(rec.Result())
        else:
            print(rec.PartialResult())

    return print(rec.FinalResult())

def speak(line):
    cmd = "./speak.sh \"{}\"".format(line)
    os.system(cmd)

# main loop
call_aida = text2speech()
speak("Hi Doctor, how can I help you?")

if call_aida == "Aida":

    first_input = text2speech()
    if first_input == "history":
        speak("The patient went through one surgery in March 2020.\
        During the surgery the second heart valve was replaced with an \
        biological valve from a cow.")

        time.sleep(2)
        second_input = text2speech()

        if second_input == "biological":
            speak("The second floor of the hospital has two biological valves available.")
            time.sleep(2)
            third_input = text2speech()

            if (third_input == "nurse") or (third_input == "employee"):
                speak("Confirm calling a nurse by hovering over the module next to the patients bed.")
                time.sleep(2)
        
        else:
            print("Something went wrong!")


    elif first_input == "occupation":
        speak("The patient works as a wholesaler and has already suffered two heart attacks.")

        time.sleep(2)
        second_b_input = text2speech()

        if second_b_input == "heart valve":
            speak("Yes, the second heart valve of the patient is artifical.")
            time.sleep(2)
            third_b_input = text2speech()

            if (third_b_input == "artifical") or (third_b_input == "biological"):
                speak("There are two artifical heart valves in the storage of the hospital.")
                time.sleep(2)

                fourth_b_input = text2speech()

                if (fourth_b_input == "nurse") or (fourth_b_input == "employee"):
                    speak("Confirm calling a nurse by hovering over the module next to the patients bed.")
                    time.sleep(2)
        else:
            print("Something went wrong!")


i2c = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_apds9960.apds9960.APDS9960(i2c)
sensor.enable_proximity = True

while True:
    prox = sensor.proximity
    if prox > 10:
        speak("Confirmation accepted. A nurse is coming.")
        break

