#!/usr/bin/env python
# Display a runtext with double-buffering.
from samplebase import SampleBase
from rgbmatrix import graphics
import time


class RunText(SampleBase):
    def __init__(self, text, *args, **kwargs):
        super(RunText, self).__init__(*args, **kwargs)
        self.text = text

    def run(self):
        offscreen_canvas = self.matrix.CreateFrameCanvas()
        font = graphics.Font()
        font.LoadFont("fonts/7x13.bdf")
        textColor = graphics.Color(255, 255, 0)
        pos = offscreen_canvas.width
        my_text = self.text

        len = graphics.DrawText(offscreen_canvas, font, pos, 18, textColor, my_text)
        while (pos + len >= 0):
            offscreen_canvas.Clear()
            len = graphics.DrawText(offscreen_canvas, font, pos, 18, textColor, my_text)
            pos -= 1

            time.sleep(0.04)
            offscreen_canvas = self.matrix.SwapOnVSync(offscreen_canvas)

# Main function
if __name__ == "__main__":
    run_text = RunText()
    if (not run_text.process()):
        run_text.print_help()
