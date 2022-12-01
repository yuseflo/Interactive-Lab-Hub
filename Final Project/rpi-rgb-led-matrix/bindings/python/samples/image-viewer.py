#!/usr/bin/env python
import time
import sys

from rgbmatrix import RGBMatrix, RGBMatrixOptions
from PIL import Image
from rgbmatrix import graphics


if len(sys.argv) < 2:
    sys.exit("Require an image argument")
else:
    image_file = sys.argv[1]

image = Image.open(image_file)

# Configuration for the matrix
options = RGBMatrixOptions()
options.rows = 32
options.cols = 64
options.chain_length = 1
options.parallel = 1
options.gpio_slowdown = 4
options.hardware_mapping = 'adafruit-hat'  # If you have an Adafruit HAT: 'adafruit-hat'

matrix = RGBMatrix(options = options)

# Make image fit our screen.
image.thumbnail((10, 10), Image.ANTIALIAS)

#matrix.SetImage(image.convert('RGB'))

pacman_corrections_black = {0: [0, 1, 2, 8, 9],
                            1: [0, 1, 9],
                            2: [0, 8, 9],
                            3: [7, 8, 9],
                            4: [6, 7, 8, 9],
                            5: [6, 7, 8, 9],
                            6: [7, 8, 9],
                            7: [0, 8, 9],
                            8: [0, 1, 9],
                            9: [0, 1, 2, 8, 9],
                            10: []}

offset_canvas = matrix.CreateFrameCanvas()
for x in range(1, 11):
    for y in range(1, 11):
        offset_canvas.SetPixel(x, y, 255, 255, 0)

for y, x_vals in pacman_corrections_black.items():
    for x in x_vals:
        offset_canvas.SetPixel(1+x, 1+y, 0, 0, 0)

heart_corrections_black = {0: [0, 3, 4, 5, 8],
                           1: [4],
                           4: [0, 8],
                           5: [0, 1, 7, 8],
                           6: [0, 1, 2, 6, 7, 8], 
                           7: [0, 1, 2, 3, 5, 6, 7, 8],
                           8: [0, 1, 2, 3, 4, 5, 6, 7, 8]}

for x in range(15, 24):
    for y in range(23, 32):
        offset_canvas.SetPixel(x, y, 255, 0, 0)

for y, x_vals in heart_corrections_black.items():
    for x in x_vals:
        offset_canvas.SetPixel(15+x, 23+y, 0, 0, 0)

font = graphics.Font()
font.LoadFont("../../../fonts/4x6.bdf")
textColor = graphics.Color(255, 255, 255)
pos = offset_canvas.width
my_text = "3x"
len = graphics.DrawText(offset_canvas, font, 4, 30, textColor, my_text)

my_text = "TILT"
len = graphics.DrawText(offset_canvas, font, 12, 21, textColor, my_text)

arrow_corrections_black = {0: [0, 1, 2, 3, 5, 6, 7, 8, 9],
                           1: [0, 1, 2, 6, 7, 8],
                           2: [0, 1, 2, 3, 5, 6, 7, 8],
                           3: [0, 2, 3, 5, 6, 8],
                           5: [0, 2, 3, 5, 6, 8],
                           6: [0, 1, 2, 3, 5, 6, 7, 8],
                           7: [0, 1, 2, 6, 7, 8],
                           8: [0, 1, 2, 3, 5, 6, 7, 8, 9]}

for x in range(1, 10):
    for y in range(13, 22):
        offset_canvas.SetPixel(x, y, 255, 255, 255)

for y, x_vals in arrow_corrections_black.items():
    for x in x_vals:
        offset_canvas.SetPixel(1+x, 13+y, 0, 0, 0)

for y in range(32):
    offset_canvas.SetPixel(29, y, 255, 255, 255)

ghost_corrections_black = {0: [0, 1, 2, 3, 4, 9, 10, 11, 12, 13],
                           1: [0, 1, 2, 11, 12, 13],
                           2: [0, 1, 12, 13],
                           3: [0, 4, 5, 10, 11, 13],
                           4: [0, 3, 4, 5, 6, 9, 10, 11, 12, 13],
                           5: [0, 3, 4, 9, 10, 13],
                           6: [3, 4, 9, 10],
                           7: [4, 5, 10, 11],
                           12: [2, 6, 7, 11],
                           13: [1, 2, 3, 6, 7, 10, 11, 12]}

ghost_corrections_white = {5: [5, 6, 11, 12],
                           6: [5, 6, 11, 12]}


for x in range(12, 26):
    for y in range(0, 14):
        offset_canvas.SetPixel(x, y, 0, 0, 255)

for y, x_vals in ghost_corrections_black.items():
    for x in x_vals:
        offset_canvas.SetPixel(12+x, y, 0, 0, 0)

for y, x_vals in ghost_corrections_white.items():
    for x in x_vals:
        offset_canvas.SetPixel(12+x, y, 255, 255, 255)

my_text = "PAC-MAN"
len = graphics.DrawText(offset_canvas, font, 33, 7, graphics.Color(255, 255, 0), my_text)

for x in range(30, 64):
    offset_canvas.SetPixel(x, 8, 255, 255, 255)

my_text = "EAT DOTS"
len = graphics.DrawText(offset_canvas, font, 31, 16, textColor, my_text)

for x in range(32, 62):
    offset_canvas.SetPixel(x, 18, 0, 0, 255)

for x in range(32, 62):
    offset_canvas.SetPixel(x, 30, 0, 0, 255)

for y in range(18, 30):
    offset_canvas.SetPixel(32, y, 0, 0, 255)

for y in range(18, 31):
    offset_canvas.SetPixel(62, y, 0, 0, 255)

offset_canvas = matrix.SwapOnVSync(offset_canvas)



try:
    print("Press CTRL-C to stop.")
    while True:
        time.sleep(100)
except KeyboardInterrupt:
    sys.exit(0)
