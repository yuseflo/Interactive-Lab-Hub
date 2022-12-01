#!/usr/bin/env python
from samplebase import SampleBase


class SimpleSquare(SampleBase):
  def __init__(self, file, *args, **kwargs):
    self.walls, self.dots, self.power_pellets, self.blanks = self.read_board_in(file)

    super(SimpleSquare, self).__init__(*args, **kwargs)

  def run(self):
    offset_canvas = self.matrix.CreateFrameCanvas()
    while True:
      for x, y in self.walls.keys():
        offset_canvas.SetPixel(x, y, 0, 0, 255)
      for x, y in self.dots.keys():
        offset_canvas.SetPixel(x, y, 255, 102, 0)
      for x, y in self.power_pellets.keys():
        offset_canvas.SetPixel(x, y, 255, 255, 255)
      offset_canvas = self.matrix.SwapOnVSync(offset_canvas)


  def read_board_in(self, filename):
    walls, dots, power_pellets, blanks = {}, {}, {}, {}
    with open(filename) as f:
      for y, line in enumerate(f):
        for x, val in enumerate(line):
          if val == "\n":
            continue
          if val == "X":
            walls[(x, y)] = True
          elif val == ".":
            dots[(x, y)] = True
          elif val == "S":
            power_pellets[(x, y)] = True
          elif val == "_":
            blanks[(x, y)] = True
          elif val == "P":
            pass
          elif val == "E":
            pass
          else:
            assert False, f"Character {val} not recognized"
    return walls, dots, power_pellets, blanks

if __name__ == "__main__":  
  file = 'pacman_board_1.txt'
  simple_square = SimpleSquare(file)
  if (not simple_square.process()):
      simple_square.print_help()