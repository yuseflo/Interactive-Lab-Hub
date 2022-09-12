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
button_press = False

while True:
    
    # Press button A
    if not buttonA.value:
        button_press = True
    
    if button_press:
        # Draw a black filled box to clear the image.
        draw.rectangle((0, 0, width, height), outline=0, fill=0)


        world = "Olympics Running"

        # Define countdown
        mins, secs = divmod(t, 20)
        timer = '{0}'.format(secs)
        t -= 1

        draw.text((0, 0), strftime("%a %d" ), font=font, fill="#F4E38E")
        draw.text((75, 0), world, font=font, fill="#F4E38E")
        draw.text((0, 110), "Countdown: {0} s".format(timer), font=font, fill="#FFFFF0")

        # Define 3 players and their position
        hash = "#"
        draw.text((x1, 32), hash, font=font, fill="#0000FF")
        ampersand = "&"
        draw.text((x2, 55), dollar, font=font, fill="#00FF00")
        dollar = "$"
        draw.text((x3, 78), ampersand, font=font, fill="#FF0000")

        x1 += 13.4
        x2 += 16.8
        x3 += 15.4

        # Let players start again after they reach the border of the display
        if x1 > 230:
            x1 = 0

        if x2 > 230:
            x2 = 0

        if x3 > 230:
            x3 = 0 

        # Display image.
        disp.image(image, rotation)
        time.sleep(1)

