# Chatterboxes
Yusef Iskandar
[![Watch the video](https://user-images.githubusercontent.com/1128669/135009222-111fe522-e6ba-46ad-b6dc-d1633d21129c.png)](https://www.youtube.com/embed/Q8FWzLMobx0?start=19)

In this lab, we want you to design interaction with a speech-enabled device--something that listens and talks to you. This device can do anything *but* control lights (since we already did that in Lab 1).  First, we want you first to storyboard what you imagine the conversational interaction to be like. Then, you will use wizarding techniques to elicit examples of what people might say, ask, or respond.  We then want you to use the examples collected from at least two other people to inform the redesign of the device.

We will focus on **audio** as the main modality for interaction to start; these general techniques can be extended to **video**, **haptics** or other interactive mechanisms in the second part of the Lab.

## Prep for Part 1: Get the Latest Content and Pick up Additional Parts 

### Pick up Web Camera If You Don't Have One

Students who have not already received a web camera will receive their [IMISES web cameras](https://www.amazon.com/Microphone-Speaker-Balance-Conference-Streaming/dp/B0B7B7SYSY/ref=sr_1_3?keywords=webcam%2Bwith%2Bmicrophone%2Band%2Bspeaker&qid=1663090960&s=electronics&sprefix=webcam%2Bwith%2Bmicrophone%2Band%2Bsp%2Celectronics%2C123&sr=1-3&th=1) on Thursday at the beginning of lab. If you cannot make it to class on Thursday, please contact the TAs to ensure you get your web camera. 

### Get the Latest Content

As always, pull updates from the class Interactive-Lab-Hub to both your Pi and your own GitHub repo. There are 2 ways you can do so:

**\[recommended\]**Option 1: On the Pi, `cd` to your `Interactive-Lab-Hub`, pull the updates from upstream (class lab-hub) and push the updates back to your own GitHub repo. You will need the *personal access token* for this.

```
pi@ixe00:~$ cd Interactive-Lab-Hub
pi@ixe00:~/Interactive-Lab-Hub $ git pull upstream Fall2022
pi@ixe00:~/Interactive-Lab-Hub $ git add .
pi@ixe00:~/Interactive-Lab-Hub $ git commit -m "get lab3 updates"
pi@ixe00:~/Interactive-Lab-Hub $ git push
```

Option 2: On your your own GitHub repo, [create pull request](https://github.com/FAR-Lab/Developing-and-Designing-Interactive-Devices/blob/2022Fall/readings/Submitting%20Labs.md) to get updates from the class Interactive-Lab-Hub. After you have latest updates online, go on your Pi, `cd` to your `Interactive-Lab-Hub` and use `git pull` to get updates from your own GitHub repo.

## Part 1.

### Text to Speech 

In this part of lab, we are going to start peeking into the world of audio on your Pi! 

We will be using the microphone and speaker on your webcamera. In the home directory of your Pi, there is a folder called `text2speech` containing several shell scripts. `cd` to the folder and list out all the files by `ls`:

```
pi@ixe00:~/text2speech $ ls
Download        festival_demo.sh  GoogleTTS_demo.sh  pico2text_demo.sh
espeak_demo.sh  flite_demo.sh     lookdave.wav
```

You can run these shell files by typing `./filename`, for example, typing `./espeak_demo.sh` and see what happens. Take some time to look at each script and see how it works. You can see a script by typing `cat filename`. For instance:

```
pi@ixe00:~/text2speech $ cat festival_demo.sh 
#from: https://elinux.org/RPi_Text_to_Speech_(Speech_Synthesis)#Festival_Text_to_Speech

echo "Just what do you think you're doing, Dave?" | festival --tts
```

Now, you might wonder what exactly is a `.sh` file? Typically, a `.sh` file is a shell script which you can execute in a terminal. The example files we offer here are for you to figure out the ways to play with audio on your Pi!

You can also play audio files directly with `aplay filename`. Try typing `aplay lookdave.wav`.

\*\***Write your own shell file to use your favorite of these TTS engines to have your Pi greet you by name.**\*\*
(This shell file should be saved to your own repo for this lab.)

I used the Google TTS engine to let the Pi greet me by my name. 

https://user-images.githubusercontent.com/91849980/192334065-51fd76e2-74cf-416a-a100-bca325b6c5bc.MOV


### Speech to Text

Now examine the `speech2text` folder. We are using a speech recognition engine, [Vosk](https://alphacephei.com/vosk/), which is made by researchers at Carnegie Mellon University. Vosk is amazing because it is an offline speech recognition engine; that is, all the processing for the speech recognition is happening onboard the Raspberry Pi. 

In particular, look at `test_words.py` and make sure you understand how the vocab is defined. 
Now, we need to find out where your webcam's audio device is connected to the Pi. Use `arecord -l` to get the card and device number:
```
pi@ixe00:~/speech2text $ arecord -l
**** List of CAPTURE Hardware Devices ****
card 1: Device [Usb Audio Device], device 0: USB Audio [USB Audio]
  Subdevices: 1/1
  Subdevice #0: subdevice #0
```
The example above shows a scenario where the audio device is at card 1, device 0. Now, use `nano vosk_demo_mic.sh` and change the `hw` parameter. In the case as shown above, change it to `hw:1,0`, which stands for card 1, device 0.  

Now, look at which camera you have. Do you have the cylinder camera (likely the case if you received it when we first handed out kits), change the `-r 16000` parameter to `-r 44100`. If you have the IMISES camera, check if your rate parameter says `-r 16000`. Save the file using Write Out and press enter.

Then try `./vosk_demo_mic.sh`

\*\***Write your own shell file that verbally asks for a numerical based input (such as a phone number, zipcode, number of pets, etc) and records the answer the respondent provides.**\*\*

For this part, it was difficult for the Pi to recognize numbers. However, I let the camera ask me how many pets I have. The corresponding video can be seen below:

https://drive.google.com/file/d/17fuoPT9_ZYEyNcnZpSeEj1g6bew4J5KR/view?usp=sharing


### Serving Pages

In Lab 1, we served a webpage with flask. In this lab, you may find it useful to serve a webpage for the controller on a remote device. Here is a simple example of a webserver.

```
pi@ixe00:~/Interactive-Lab-Hub/Lab 3 $ python server.py
 * Serving Flask app "server" (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: on
 * Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 162-573-883
```
From a remote browser on the same network, check to make sure your webserver is working by going to `http://<YourPiIPAddress>:5000`. You should be able to see "Hello World" on the webpage.

The hello world example worked for me and can be seen below:

<img width="361" alt="Screen Shot 2022-09-26 at 12 49 54 PM" src="https://user-images.githubusercontent.com/91849980/192335176-12dd0e4d-0fe3-41c8-9dc2-cd245535a57c.png">


### Storyboard

Storyboard and/or use a Verplank diagram to design a speech-enabled device. (Stuck? Make a device that talks for dogs. If that is too stupid, find an application that is better than that.) 

\*\***Post your storyboard and diagram here.**\*\*

I designed a smart surgery assistant that helps surgeons execute surgeries without the help of nurses. During a surgery, the doctor wears gloves and is often not able to use the computer to gather information about the patient and maybe also specific information about human organs. The smart device provides the doctor with the health record of the patient as well as with information about materials in the hospital. The device is also able to contact a nurse, in case the doctor needs some help.   

![Lab-17](https://user-images.githubusercontent.com/91849980/192410833-35161c89-f981-4be0-bc61-a2a81c1258d6.jpg)
![Lab-19](https://user-images.githubusercontent.com/91849980/192410866-cb16f3a2-1af4-4103-86f6-4b5138ca3e03.jpg)


Write out what you imagine the dialogue to be. Use cards, post-its, or whatever method helps you develop alternatives or group responses. 

\*\***Please describe and document your process.**\*\*

Since a doctor is during a surgery under time pressure, he probably needs information very fast and concise, which the smart device can definitely provide. In this case I was thinking of a heart surgery, where the doctor identifies during the surgery that another doctor already executed an operation on the patient's heart. To be aware what the previous doctor did, our technology called "Aida" will provide the surgeon with the requested information. In order to go one step beyond and replace a heart valve, the doctor needs material, where again Aida assists the doctor by giving him information about the availability of the requested heart valve.  

![Lab-18](https://user-images.githubusercontent.com/91849980/192410841-bc2cfa18-5e2f-4f1b-8bb7-3eb4537fba90.jpg)


### Acting out the dialogue

Find a partner, and *without sharing the script with your partner* try out the dialogue you've designed, where you (as the device designer) act as the device you are designing.  Please record this interaction (for example, using Zoom's record feature).

\*\***Describe if the dialogue seemed different than what you imagined when it was acted out, and how.**\*\*

One thing I did not consider was that the doctor said "Aida" and the actual command at the same time, which did not give Aida enough time to greet the doctor and then answer the doctor's question. In general, it seems technically difficult to implement the consideration of the trigger word and the actual command. Also, in the end when the doctor hovered over the sensor, there should be a visual or auditory signal that lets the doctor know, that the sensor received a signal.  

https://drive.google.com/file/d/10EUUjv0IRVOnlmkGHxwBIJH486OmxNVn/view?usp=sharing


# Lab 3 Part 2

For Part 2, you will redesign the interaction with the speech-enabled device using the data collected, as well as feedback from part 1.

*Document how the system works*

*Include videos or screencaptures of both the system and the controller.*

For the second part of this Lab I kept working on my smart surgery assistant that helps surgeons execute surgeries without the help of nurses. The idea is that during a surgery the doctor wears gloves and is often not able to use the computer to gather information about the patient. The smart device provides the doctor with the health record of the patient as well as with information about materials in the hospital. The device is also able to contact a nurse, in case the doctor needs some help. To confirm calling a nurse we use a proximity sensor. The doctor only has to hover over the controller to confirm that "Aida" is calling a nurse.

In the following I created two different storyboards where two different scenarios are displayed. Both scenarios are tested with two different users in the two different videos that can be seen in the end of the Lab.  

![Lab-20](https://user-images.githubusercontent.com/91849980/193710360-862cf31d-abc9-46e2-b56a-ec090ac8a05f.jpg)
![Lab-18](https://user-images.githubusercontent.com/91849980/193710358-543fb3c0-4271-4084-9909-2011eb59debe.jpg)
![Lab-21](https://user-images.githubusercontent.com/91849980/193710361-3a197cbd-f6a4-43f1-9dd8-7f4a7f68aef1.jpg)
![Lab-22](https://user-images.githubusercontent.com/91849980/193710362-fc87d5c0-9cf2-4d1f-a609-9d65d1148bde.jpg)
![Lab-19](https://user-images.githubusercontent.com/91849980/193710359-51634c6f-5287-4ed7-a688-f303bddfd3cd.jpg)

The image below demonstrates the system and the controller. 

![setup](https://user-images.githubusercontent.com/91849980/193711037-6f6ba183-60dd-4692-a972-e4171a5720f5.jpg)

*Videos*

User Interaction 1:

https://drive.google.com/file/d/1r7jzRDJr4C-6k_DcgnufoaPBXdchQ7GN/view?usp=sharing

User Interaction 2:

https://drive.google.com/file/d/1N4-d9oEZVs9SRWg8I-WRFClDzxkix1ke/view?usp=sharing


## Test the system
Try to get at least two people to interact with your system. (Ideally, you would inform them that there is a wizard _after_ the interaction, but we recognize that can be hard.)

The 2 videos can be seen above.

Answer the following:

### What worked well about the system and what didn't?

The good thing about the system is its detection of the trigger word which was pretty accurate. Although there was some background noise in the first video, Aida was still able to interact with the user. The two videos demonstrate two different scenarios on how to interact with the system which worked pretty good. Since Aida has multiple functionalities, the problem with the system was that it captures only a small number of scenarios of how the doctor interacts with the system. 

### What worked well about the controller and what didn't?

The controller is important since the doctor may just brainstorm by himself on what he could do in the situation of a surgery. Confirming calling a nurse by using the controller adds more seriousness to his request. Unfortunately, when the users were interacting with the proximity sensor, they had to flex their knees and try to hover over the sensor multiple times considering different distances to the sensor. This can be fixed by changing the distance parameter of the sensor which will make the interaction with users way easier. 

### What lessons can you take away from the WoZ interactions for designing a more autonomous version of the system?

There are two main lessons I took away from the WoZ interactions. The first one deals with the quantity of information Aida gives the doctor after asking a question. During a surgery, the doctor needs information very quick which may be a problem with how fast Aida speaks and also with how much information Aida actually provides to answer a specific question. The second lesson is more related to the flexibility between the two scenarios I recorded. Unfortunately, combining both scenarios to make the system more autonomous is technically hard to implement. Therefore, the interactions should rather kept simple. 


### How could you use your system to create a dataset of interaction? What other sensing modalities would make sense to capture?

In general, I could have probably used a camera instead of the proximity sensor to call staff/nurse. By using a camera that automatically detects whether the doctor is raising his hand, the doctor does not need to come close to the controller which saves him time during the operation. It will also fulfill our requirement that the doctor does not need to touch anything because in an operation he wears gloves which should not accumulate bacteria. 
