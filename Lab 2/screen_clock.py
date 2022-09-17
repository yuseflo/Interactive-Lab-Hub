from pickle import TRUE
from time import strftime, sleep
import time
import subprocess
import digitalio
import board
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.st7789 as st7789
from adafruit_rgb_display.rgb import color565
import webcolors
import random

# Configuration for CS and DC pins (these are FeatherWing defaults on M0/M4):
cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = None

# Config for display baudrate (default max is 24mhz):
BAUDRATE = 64000000

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
# Move left to right keeping track of the current x position for drawing shapes.
x = 0

# Alternatively load a TTF font.  Make sure the .ttf font file is in the
# same directory as the python script!
# Some other nice fonts to try: http://www.dafont.com/bitmap.php
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
font_big = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)

# Turn on the backlight
backlight = digitalio.DigitalInOut(board.D22)
backlight.switch_to_output()
backlight.value = True
buttonA = digitalio.DigitalInOut(board.D23)
buttonB = digitalio.DigitalInOut(board.D24)

# Initialize x-position of the 3 players
x1 = 0
x2 = 0
x3 = 0

# Initialize time for countdown
t = 0

# Declare value to indicate if button is pressed once or not
button_marathon = False

button_seconds = False

while True:
    
    # Display menu
    draw.rectangle((0, 0, width, height/2), outline=0, fill="#0000FF")
    draw.rectangle((0, height, width, height/2), outline=0, fill="#FFFFFF")
    draw.text((25,20), "Watch Marathon", font=font_big, fill="#FFFFFF")
    draw.text((75,80), "Settings", font=font_big, fill="#000000")

    # Press button A
    if not buttonA.value:
        button_marathon = True
    
    if button_marathon:
        # Draw a black filled box to clear the image.
        draw.rectangle((0, 0, width, height), outline=0, fill=0)
        
        # Draw menu to select countdown
        draw.rectangle((0, 0, width, height/2), outline=0, fill="#0000FF")
        draw.rectangle((0, height, width, height/2), outline=0, fill="#FFFFFF")
        draw.text((75,20), "10 sec", font=font_big, fill="#FFFFFF")
        draw.text((75,80), "20 sec", font=font_big, fill="#000000")

        # Select 20 sec
        if not buttonB.value:
            button_seconds = True
        
        if button_seconds: 
            
            draw.rectangle((0, 0, width, height), outline=0, fill=0)

            world = "Olympics Marathon"

            # Define countdown
            mins, secs = divmod(t, 20)
            timer = '{:.2f}'.format(float(secs))
            t -= 0.1

            # Draw countdown bar at the bottom of the screen
            draw.text((0, 0), strftime("%a %d" ), font=font, fill="#F4E38E")
            draw.text((75, 0), world, font=font_small, fill="#F4E38E")
            draw.text((0, 110), "Countdown: {0} s".format(timer), font=font, fill="#FFFFF0")

            # Define 3 players and their position
            hash = "#"
            draw.text((x1, 32), hash, font=font, fill="#0000FF")
            ampersand = "$"
            draw.text((x2, 55), ampersand, font=font, fill="#00FF00")
            dollar = "&"
            draw.text((x3, 78), dollar, font=font, fill="#FF0000")

            # Define random movement of the players
            x1 += random.randrange(2, 7)
            x2 += random.randrange(2, 7)
            x3 += random.randrange(2, 7)

            # Let players start again after they reach the border of the display
            if x1 > 230:
                x1 = 0

            if x2 > 230:
                x2 = 0

            if x3 > 230:
                x3 = 0
            
            # Display winner when the countdown ends
            if round(t, 1) <= -20.200:
                draw.rectangle((0, 0, width, height), outline=0, fill=0)
                draw.text((80,20), "Winner:", font=font_big, fill="#FFFFFF")

                if x1 > x2 and x3:
                    draw.text((120,50), "#", font=font_big, fill="#0000FF")
                elif x2 > x1 and x3:
                    draw.text((120,50), "$", font=font_big, fill="#00FF00")
                elif x3 > x1 and x2:
                    draw.text((120,50), "&", font=font_big, fill="#FF0000")
                
                time.sleep(3)
                
        

    # Display image.
    disp.image(image, rotation)
    time.sleep(0.1)

