# Final Project: Matrix Gaming Console

**NAMES OF COLLABORATORS HERE** Rahul Jain, Yusef Iskandar

## Project Plan

<img src="imgs/pitch_slide.png" alt="Pitch slide"/>


### Project Big Idea

The idea is to create an interactive RGB matrix panel on which the user can play games. The difference from conventional games is that the angular movement of the matrix panel is detected by a gyroscope and displayed in the game. Additionally, capacitive sensors and a microphone will be used to allow the user to control special aspects of the game with touch or their voice. 

Potential games ideas:
* Pacman:
  * Gyroscope: Side to side tilt to move the player left to right
  * Capacitive sensors: press for activating features like 2x speed
  * Microphone: if the user is close to dying, they can yell (and press and hold the capacitive sensor) and activate a random teleport feature which moves them around the board; but it also reduces their score
* Maze:
  * Gyroscope: Side to side tilt to move the marble left to right
  * Capacitive sensors: reset and start from initial point
  * Microphone: Loud sound unlocks a hidden passage (moves walls around), but it reduces their score
* Tetris:
  * Gyroscope: Side to side tilt to move the pieces left to right
  * Capacitive sensors: Rotate orientation of pieces
  * Microphone: Loud sound unlocks a hidden passage (moves walls around), but it reduces their score
* Others: Snake, Brick Breaker, Etch-a-sketch

<img src="imgs/storyboard.png" alt="Storyboard"/>

<img src="imgs/verplank.png" alt="Verplank"/>

### Project Timeline

* WEEK 12: Concept Design
  * Brainstorming ideas and developing the interaction
  * Storyboarding + Verplank Diagrams
* WEEK 13: Physical Hardware Development
  * Nov 15: Ordered parts arrive
  * Testing functionality of individual components (Matrix panel, Gyroscope, Capacitive sensor, Microphone)
    * Gyroscope calibration
  * Soldering + Wiring components + Power
    * Solder gyroscope connection onto the matrix bonnet
    * Connect gyroscope / capacitive sensor over I2C bus
  * Create a cardboard + acrylic casing
    * Take measurements / account for spacing of components (including Pi, sensors, power cables)
    * Create holes for power cables / heat vent
* WEEK 14: Software Development
  * Test gyroscope, capacitive sensor interaction
  * Design home screen for the games + games themselves
  * Test with users
* WEEK 15 / 16:
  * Cleaning up code; documenting process


### Parts Needed

* Matrix Power supply 5V 4A - $15
  * https://www.mouser.com/ProductDetail/485-1466 
* Matrix Panel - $40
  * https://www.mouser.com/ProductDetail/485-2278 
* Matrix Bonnet - $15
  * https://www.mouser.com/ProductDetail/485-3211 
* Female DC Power Adapter - $2
  * https://www.mouser.com/ProductDetail/485-368 
* Gyroscope: MPU 6050 6 DoF - $13
  * https://www.mouser.com/ProductDetail/485-3886
* USB Microphone - $8
  * https://www.amazon.com/SunFounder-Microphone-Raspberry-Recognition-Software/dp/B01KLRBHGM 
* Raspberry Pi 3B+ - Have in the class kit
* StemmaQT Cables - Have in the class kit
* Capacitive Touch Sensor - Have in the class kit
* Raspberry Pi Power supply - Have in the class kit

### Risks / contingencies

One of the biggest risks for our idea is that the parts ordered turn out to be defective. Specifically, if any one of the matrix panels, matrix bonnet, or power supply turns out to be faulty, we will need to reorder parts which can take time. Another risk is that something unexpected arises when we try to make connections between the components. In general, our project plan is somewhat ambitious for the time frame as there are a lot of unknowns with both the hardware and software.

### Fall-back plan

One fall-back plan to mitigate the risk that the parts are defective is that we use any display we have and connect it with a HDMI cable to the raspberry pi. Another idea could be to use the gyroscope in an old mobile phone or a separate handheld controller (separate RPi) and stream the data to the display. To mitigate the risk of the unknowns in our project, we will focus on the core implementation first, which includes developing the main interaction components, before moving on to more complex things like creating better graphics / complex game logic.

## Functional Checkoff 

The video for the functional checkoff is below. The video shows the matrix gaming console with Pacman implemented on it. The main interaction components that are shown include tilting the board to move pacman around as well as the volume level detection which impacts the speed of the game. Additionally, we have included some more sketches and photographs from the work we have done so far in the subsequent sections.

[![Final Project Functional Checkoff](https://img.youtube.com/vi/FJsH19XHq3g/0.jpg)](https://www.youtube.com/watch?v=FJsH19XHq3g)

### Revised concept design for Pacman

The storyboard for Pacman is below. From the project plan we modified the idea to include the following components:
* Gyroscope: Side to side tilt to move the player left to right
* Microphone: Loud volume = faster game speed, Quieter volume = slower game speed; a faster game speed makes it harder to execute precise maneuvers around the walls
* Speaker (in progress): Special game states like pacman death, eating a ghost, game over have audio feedback to tell the user that they have occurred

<img src="imgs/storyboard_pacman.png" alt="Storyboard Pacman"/>

### Physical Hardware Development

Below are some images from connecting the physical components, wiring, soldering, and casing design.

<img src="imgs/hardware_wiring2.png" alt="Hardware" width=400/>

<img src="imgs/hardware_wiring.png" alt="Hardware" width=400/>

<img src="imgs/hardware_soldering_bonnet.png" alt="Hardware" width=400/>

Cardboard / Acryllic case design [file](./imgs/final_box_design.ai):

<img src="imgs/hardware_cardboard_casing.png" alt="Hardware" width=400/>

<img src="imgs/hardware_casing.png" alt="Hardware" width=400/>

### Software Development

Below are some images from inital testing of the matrix panel.

Creating and displaying an intuitive homescreen:

<img src="imgs/software_homescreen.png" alt="Software" width=400/>

Parsing a simple maze file and displaying it. Maze Files [1](pacman_board_1.txt), [2](pacman_board_2.txt), [3](pacman_board_3.txt).

<img src="imgs/software_dev_testing_maze_display.png" alt="Software" width=400/>

Taping a gyroscope to a box to test its functionality individually:

<img src="imgs/software_testing_gyroscope.png" alt="Software" width=400/>

Here is a behind-the-scenes video for some testing of the gyroscope readings and the progression towards moving the Pacman around the board.

[![Final Project Gyro Behind the Scenes](https://img.youtube.com/vi/jXzmlWeQkb0/0.jpg)](https://www.youtube.com/watch?v=jXzmlWeQkb0)

The main code for the project is located in [pacman.py](pacman.py) which has dependencies in [pacman_sensors.py](pacman_sensors.py), [sample_base.py](samplebase.py) and a few other library files.

The initial testing files and other debugging files that we used are: [gyroscope_test.py](gyroscope_test.py), [led_panel_test.py](led_panel_test.py), [runtext.py](runtext.py), and [integration_test.py](integration_test.py).
