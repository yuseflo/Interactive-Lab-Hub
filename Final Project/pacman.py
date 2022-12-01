#!/usr/bin/env python
from samplebase import SampleBase # seperate file
from runtext import RunText
import adafruit_mpu6050, board, math, time, threading, random
from queue import Queue
from rgbmatrix import graphics
import pacman_sensors # my file

SKIP_HOMESCREEN = False

class MatrixPanel(SampleBase):
  def __init__(self, mpu_queue, volume_queue, *args, **kwargs):
    super(MatrixPanel, self).__init__(*args, **kwargs)
    self.mpu_queue = mpu_queue
    self.volume_queue = volume_queue
    self.game = PacmanGame() # configure this if we want multiple games
    self.offset_canvas = None # init elsewhere

  def run(self):
    self.offset_canvas = self.matrix.CreateFrameCanvas()
    run_again = False
    while True:
      # First do the home screen stuff
      if not SKIP_HOMESCREEN and not run_again:
        self.game.display_home_screen(self, mpu_queue)
        run_again = True
      # When that is done, show the game board
      self.game.init_board(self)
      while not self.game.game_over:
        # Get the inputs synchronously
        pitch, roll = self.get_mpu_pitch_roll()
        volume_level = self.get_volume_level()

        # Update the game state and screen, every game should have a main function
        self.game.update_game_state(self, pitch, roll, volume_level)
        time.sleep(self.game.game_speed)

      # Game is over; go back to home screen
      self.game = PacmanGame() # reset the game state


  def get_mpu_pitch_roll(self):
    return self.mpu_queue.get()
  
  def get_volume_level(self):
    # should influence the pacman speed somewhere after calling this function
    return self.volume_queue.get()


class PacmanGame():
  LIVES_COLOR = (255, 0, 0) # RED
  SCORE_COLOR = (255, 255, 0) # YELLOW 
  WALL_COLOR = (0, 0, 255) # BLUE
  FOOD_COLOR = (255, 255, 255) # WHITE
  POWER_PELLETS_COLOR = (0, 255, 0)# GREEN
  PACMAN_COLOR = (255, 255, 0) # YELLOW 

  ENEMY_BLINKY_COLOR = (255, 0, 0) # RED
  #ENEMY_PINKY_COLOR = (255, 184, 255) # PINK
  #ENEMY_INKY_COLOR = (0, 255, 255) # AQUA
  #ENEMY_FUNKY_COLOR = (0, 255, 0) # GREEN
  #ENEMY_SUE_COLOR = (128, 0, 128) # PURPLE
  #ENEMY_CLYDE_COLOR = (255, 184, 82) # ORANGE

  #GHOST_BLINKY_COLOR = (255, 127, 127) # LIGHT RED
  #GHOST_PINKY_COLOR = (255, 182, 193) # LIGHT PINK
  #GHOST_INKY_COLOR = (203, 255, 245) # LIGHT AQUA
  #GHOST_FUNKY_COLOR = (144, 238, 144) # LIGHT GREEN
  GHOST_SUE_COLOR = (128, 0, 128) # PURPLE (203, 195, 227) # LIGHT PURPLE
  #GHOST_CLYDE_COLOR = (255, 213, 128) # LIGHT ORANGE
  
  ENEMY_COLORS = [ENEMY_BLINKY_COLOR, ENEMY_BLINKY_COLOR, ENEMY_BLINKY_COLOR, ENEMY_BLINKY_COLOR]
  GHOST_COLORS = [GHOST_SUE_COLOR, GHOST_SUE_COLOR, GHOST_SUE_COLOR, GHOST_SUE_COLOR]

  GAME_BOARD_LENGTH = 62 # leave 2 pixel cols on right side for score / lives
  GAME_BOARD_HEIGHT = 32

  PACMAN_BOARD = 'pacman_board_3.txt'

  # This is calibrated based on how the user is supposed to hold the device
  PITCH_THRESHOLD = -25
  ROLL_THRESHOLD = 7

  def __init__(self):
    self.walls, self.food, self.power_pellets, self.jail, self.pacman_init, self.enemies_init = self.read_board_in(PacmanGame.PACMAN_BOARD)
    self.pacman, self.enemies = self.pacman_init, self.enemies_init.copy()
    self.score = 0
    self.lives = 3
    self.level = 1 # the game level the player is on, each time they "beat" the game, this increases...
    self.level_phase = 0 # the game level phase the player is in; progresses from 1 to 4 so the longer they wait the harder it becomes
    self.game_speed = 0.05 # seconds; this is influenced by the volume level
    self.ghosts_active = False # the position of ghosts and enemies is tracked by the same self.enemies
    self.ghosts_timesteps_left = -1 # Ghosts timesteps left, only used if ghosts are active
    self.switch_direction = False # whether there is a transition between ghost / enemy mode currently
    self.scatter_timer = {i: -1 for i in self.enemies.keys()} # map from enemy_idx to the number of timesteps left on its scatter mode
    self.game_over = False

  def display_home_screen(self, matrix_panel, mpu_queue):
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

    for x in range(1, 11):
      for y in range(1, 11):
        matrix_panel.offset_canvas.SetPixel(x, y, 255, 255, 0)

    for y, x_vals in pacman_corrections_black.items():
      for x in x_vals:
        matrix_panel.offset_canvas.SetPixel(1+x, 1+y, 0, 0, 0)

    heart_corrections_black = {0: [0, 3, 4, 5, 8],
                              1: [4],
                              4: [0, 8],
                              5: [0, 1, 7, 8],
                              6: [0, 1, 2, 6, 7, 8], 
                              7: [0, 1, 2, 3, 5, 6, 7, 8],
                              8: [0, 1, 2, 3, 4, 5, 6, 7, 8]}

    for x in range(15, 24):
      for y in range(23, 32):
        matrix_panel.offset_canvas.SetPixel(x, y, 255, 0, 0)

    for y, x_vals in heart_corrections_black.items():
      for x in x_vals:
        matrix_panel.offset_canvas.SetPixel(15+x, 23+y, 0, 0, 0)

    font = graphics.Font()
    font.LoadFont("fonts/4x6.bdf")
    textColor = graphics.Color(255, 255, 255)
    pos = matrix_panel.offset_canvas.width
    my_text = "3x"
    len = graphics.DrawText(matrix_panel.offset_canvas, font, 4, 30, textColor, my_text)

    my_text = "TILT"
    len = graphics.DrawText(matrix_panel.offset_canvas, font, 12, 21, textColor, my_text)

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
        matrix_panel.offset_canvas.SetPixel(x, y, 255, 255, 255)

    for y, x_vals in arrow_corrections_black.items():
      for x in x_vals:
        matrix_panel.offset_canvas.SetPixel(1+x, 13+y, 0, 0, 0)

    for y in range(32):
      matrix_panel.offset_canvas.SetPixel(29, y, 255, 255, 255)

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
        matrix_panel.offset_canvas.SetPixel(x, y, 0, 0, 255)

    for y, x_vals in ghost_corrections_black.items():
      for x in x_vals:
        matrix_panel.offset_canvas.SetPixel(12+x, y, 0, 0, 0)

    for y, x_vals in ghost_corrections_white.items():
      for x in x_vals:
        matrix_panel.offset_canvas.SetPixel(12+x, y, 255, 255, 255)

    my_text = "PAC-MAN"
    len = graphics.DrawText(matrix_panel.offset_canvas, font, 33, 7, graphics.Color(255, 255, 0), my_text)
    # fix the 'N'
    matrix_panel.offset_canvas.SetPixel(57, 2, 255, 255, 0)
    matrix_panel.offset_canvas.SetPixel(59, 6, 255, 255, 0)


    for x in range(30, 64):
      matrix_panel.offset_canvas.SetPixel(x, 8, 255, 255, 255)

    my_text = "EAT DOTS"
    len = graphics.DrawText(matrix_panel.offset_canvas, font, 31, 16, textColor, my_text)

    for x in range(32, 62):
      matrix_panel.offset_canvas.SetPixel(x, 18, 0, 0, 255)

    for x in range(32, 62):
      matrix_panel.offset_canvas.SetPixel(x, 30, 0, 0, 255)

    for y in range(18, 30):
      matrix_panel.offset_canvas.SetPixel(32, y, 0, 0, 255)

    for y in range(18, 31):
      matrix_panel.offset_canvas.SetPixel(62, y, 0, 0, 255)

    homescreen_food = {(37, 28):True, (42, 20):True, (55, 27):True, (60, 21):True}

    for x, y in homescreen_food.keys():
      matrix_panel.offset_canvas.SetPixel(x, y, *PacmanGame.FOOD_COLOR)

    pacman = (45, 26)
    matrix_panel.offset_canvas.SetPixel(*pacman, *PacmanGame.PACMAN_COLOR)

    matrix_panel.matrix.SwapOnVSync(matrix_panel.offset_canvas)

    walls = dict([((i, 18), True) for i in range(32, 62)] + [((i, 30), True) for i in range(32, 62)] + 
                 [((32, j), True) for j in range(18, 30)] + [((62, j), True) for j in range(18, 31)])
    
    while list(homescreen_food.keys()) != []: #len(homescreen_food.keys()) != 0: # TODO this dict is oddly being interpreted as an integer?
      pitch, roll = matrix_panel.get_mpu_pitch_roll()
      x_old, y_old = pacman

      if abs(pitch - PacmanGame.PITCH_THRESHOLD) > abs(roll - PacmanGame.ROLL_THRESHOLD):
        x = x_old
        y = (y_old + 1) if pitch < PacmanGame.PITCH_THRESHOLD else (y_old - 1)
      else:
        x = (x_old + 1) if roll < PacmanGame.ROLL_THRESHOLD else (x_old - 1)
        y = y_old

      if (x, y) not in walls:
        matrix_panel.offset_canvas.SetPixel(x, y, *PacmanGame.PACMAN_COLOR)
        matrix_panel.offset_canvas.SetPixel(x_old, y_old, 0, 0, 0)
        matrix_panel.matrix.SwapOnVSync(matrix_panel.offset_canvas)

        pacman = (x, y)
        # Only have to check if food was eaten when there was movement
        if (x, y) in homescreen_food:
          homescreen_food.pop((x, y))

      time.sleep(self.game_speed)
    
    # Home screen is done, show the 3 ... 2 ... 1 ... GO countdown
    matrix_panel.offset_canvas.Clear()
    font = graphics.Font()
    font.LoadFont("fonts/7x13.bdf")
    textColor = graphics.Color(255, 255, 255)
    my_text = "3"
    len = graphics.DrawText(matrix_panel.offset_canvas, font, 29, 18, textColor, my_text)
    time.sleep(1.0)
    matrix_panel.offset_canvas.Clear()

    my_text = "2"
    len = graphics.DrawText(matrix_panel.offset_canvas, font, 29, 18, textColor, my_text)
    time.sleep(1.0)
    matrix_panel.offset_canvas.Clear()

    my_text = "1"
    len = graphics.DrawText(matrix_panel.offset_canvas, font, 29, 18, textColor, my_text)
    time.sleep(1.0)
    matrix_panel.offset_canvas.Clear()

    my_text = "GO"
    len = graphics.DrawText(matrix_panel.offset_canvas, font, 26, 18, textColor, my_text)
    time.sleep(1.0)
    matrix_panel.offset_canvas.Clear()

  def read_board_in(self, filename):
    walls, food, power_pellets, jail = {}, {}, {}, {}
    pacman = None
    enemies = {}
    enemy_idx = 0
    with open(filename) as f:
      for y, line in enumerate(f):
        for x, val in enumerate(line):
          if x < 0 or x > PacmanGame.GAME_BOARD_LENGTH or y < 0 or y > PacmanGame.GAME_BOARD_HEIGHT:
            continue
          if val == "\n":
            continue
          if val == "X":
            walls[(x, y)] = True
          elif val == ".":
            food[(x, y)] = True
          elif val == "S":
            power_pellets[(x, y)] = True
          elif val == " ":
            jail[(x, y)] = True
          elif val == "P":
            pacman = (x, y)
          elif val == "E":
            enemies[enemy_idx] = [(x, y), (x, y)] # mapping from enemy idx to (current position, old position)
            enemy_idx += 1
          elif val == "_":
            pass # blank space means there is no food, enemy, jail, etc on that square
          else:
            assert False, f"Character {val} not recognized"
    assert pacman != None, "Pacman has not been initialized"
    return walls, food, power_pellets, jail, pacman, enemies

  def update_game_state(self, matrix_panel, pitch, roll, volume_level):
    # Main function that takes input and makes changes to the game state based on inputs

    # Change the game speed based on the volume level 0.05 (fast speed = high volume) to 0.3 (slow speed = low volume)
    # fixed vals scheme: > 70 = high, < 25 = low, middle
    # smooth function scheme: roughly > 100 capped at 0.05; < 10 capped at 0.4
    self.game_speed = max(0, volume_level * (0.01 - 0.04) / (100 - 10) + 0.06)

    # within a level, change the scatter timer for the enemies based on what phase we are in
    # phase time = (max(0, X - 4*(self.level-1)))
    # phase 1 = 4 scatter, 0 chasing for int(phase_time * 1.3)
    # phase 2 = 3 scatter, 1 chasing for int(phase time * 1.2) 
    # phase 3 = 2 scatter, 2 chasing for int(phase time * 1.1) 
    # phase 4 = 1 scatter, 3 chasing for int(phase time * 1.0) 
    # phase 5 = 0 scatter, 4 chasing till end of level
    if sum(self.scatter_timer.values()) == -len(self.enemies) and self.level_phase != 5: # if scatter timers expired and not in last phase
      self.level_phase += 1
      phase_coeff = 1.4 - self.level_phase / 10
      phase_time = int(max(0, 100 - 4*(self.level-1)) * phase_coeff) if self.level_phase != 5 else -1
      self.scatter_timer = {i: -1 if i < self.level_phase-1 else phase_time for i in self.enemies.keys()}
   
    # First update the Pacman position based on the pitch / roll
    self.move_pacman(matrix_panel, pitch, roll)

    # Then have the Enemy/Ghost AI update their positions
    if self.ghosts_active:
      self.move_ghosts(matrix_panel)
      self.switch_direction = False
      self.ghosts_timesteps_left -= 1
      if self.ghosts_timesteps_left == 0:
        self.ghosts_active = False
        #self.switch_direction = True
        self.free_ghosts_from_jail(matrix_panel)
    else:
      self.move_enemies(matrix_panel)
      #self.switch_direction = False
    
    # Finally check if the "level" has been cleared
    if len(self.food) == 0 and len(self.power_pellets) == 0:
      self.level += 1
      self.init_board(matrix_panel)


  def init_board(self, matrix_panel, reset=False):
    # Called when the matrix panel is first booting up the game OR after a death OR if you clear a level
    # reset flag is only True for after a death
    if not reset:
      for x, y in self.walls.keys():
        matrix_panel.offset_canvas.SetPixel(x, y, *PacmanGame.WALL_COLOR)
      self.update_lives_display(matrix_panel, init=True)
    for x, y in self.food.keys():
      matrix_panel.offset_canvas.SetPixel(x, y, *PacmanGame.FOOD_COLOR)
    for x, y in self.power_pellets.keys():
      matrix_panel.offset_canvas.SetPixel(x, y, *PacmanGame.POWER_PELLETS_COLOR)

    if reset:
      # Clear the pacman's old position
      x_old, y_old = self.pacman
      matrix_panel.offset_canvas.SetPixel(x_old, y_old, 0, 0, 0)
      # Clear the enemies old position
      for (enemy_idx, coords), enemy_color in zip(self.enemies.items(), PacmanGame.ENEMY_COLORS):
        x, y = coords[0]
        if (x, y) in self.food:
          matrix_panel.offset_canvas.SetPixel(x, y, *PacmanGame.FOOD_COLOR)
        elif (x, y) in self.power_pellets:
          matrix_panel.offset_canvas.SetPixel(x, y, *PacmanGame.POWER_PELLETS_COLOR)
        elif (x, y) != self.pacman_init: # only reset if not in pacman's start
          matrix_panel.offset_canvas.SetPixel(x, y, 0, 0, 0)
    
    # Set the pacman's current position
    matrix_panel.offset_canvas.SetPixel(*self.pacman_init, *PacmanGame.PACMAN_COLOR)
    
    # Set the enemies current position
    for (enemy_idx, coords), enemy_color in zip(self.enemies_init.items(), PacmanGame.ENEMY_COLORS):
      x, y = coords[0]
      matrix_panel.offset_canvas.SetPixel(x, y, *enemy_color)
    matrix_panel.matrix.SwapOnVSync(matrix_panel.offset_canvas)

  def move_pacman(self, matrix_panel, pitch, roll):
    x_old, y_old = self.pacman
    if abs(pitch - PacmanGame.PITCH_THRESHOLD) > abs(roll - PacmanGame.ROLL_THRESHOLD):
      x = x_old
      y = (y_old + 1) % PacmanGame.GAME_BOARD_HEIGHT if pitch < PacmanGame.PITCH_THRESHOLD else (y_old - 1) % PacmanGame.GAME_BOARD_HEIGHT
    else:
      x = (x_old + 1) % PacmanGame.GAME_BOARD_LENGTH if roll < PacmanGame.ROLL_THRESHOLD else (x_old - 1) % PacmanGame.GAME_BOARD_LENGTH 
      y = y_old

    if (x, y) not in self.walls and (self.check_in_enemies_ghosts(x, y) == -1 or self.ghosts_active):
      matrix_panel.offset_canvas.SetPixel(x, y, *PacmanGame.PACMAN_COLOR)
      matrix_panel.offset_canvas.SetPixel(x_old, y_old, 0, 0, 0)
      matrix_panel.matrix.SwapOnVSync(matrix_panel.offset_canvas)

      self.pacman = (x, y)
      # Only have to update the score if there was movement
      self.update_score(matrix_panel, x, y)
    elif (self.check_in_enemies_ghosts(x, y) != -1 or ((x, y) in self.walls and self.check_in_enemies_ghosts(x_old, y_old) != -1)) and not self.ghosts_active:
      self.update_lives_display(matrix_panel)
      self.lives -= 1
      if self.lives == 0:
        # Game over
        self.display_final_score(matrix_panel)
        self.game_over = True
      else:
        # Reset the board
        self.init_board(matrix_panel, reset=True)
        # Update the pacman's active position
        self.pacman = self.pacman_init
        # Update the enemies active position
        self.enemies = self.enemies_init.copy()
    elif (self.check_in_enemies_ghosts(x, y) != -1 or ((x, y) in self.walls and self.check_in_enemies_ghosts(x_old, y_old) != -1)) and self.ghosts_active:
      # put ghost in jail
      ghost_idx = self.check_in_enemies_ghosts(x, y)

      ghost_x, ghost_y = random.choice(list(self.jail.keys()))

      self.enemies[ghost_idx] = [(ghost_x, ghost_y), (ghost_x, ghost_y)]

      # allowed to update the pacman's active position
      matrix_panel.offset_canvas.SetPixel(x, y, *PacmanGame.PACMAN_COLOR)
      matrix_panel.offset_canvas.SetPixel(x_old, y_old, 0, 0, 0)
      matrix_panel.matrix.SwapOnVSync(matrix_panel.offset_canvas)
      if (x, y) not in self.walls:
        self.pacman = (x, y)
      else:
        self.pacman = (x_old, y_old)

  def update_score(self, matrix_panel, x, y):
    # Only check if the movement was into a food or power pellet square
    # Also remove (x, y) from the food or power pellets dict
    if (x, y) in self.food:
      self.score += 10
      self.food.pop((x, y))
      self.update_score_display(matrix_panel)
    elif (x, y) in self.power_pellets:
      self.score += 50
      self.power_pellets.pop((x, y))
      self.ghosts_active = True
      self.switch_direction = True
      self.ghosts_timesteps_left = max(0, 20 - 4*(self.level-1)) # lvl 1 = 20, 2 = 16, 3 = 12, 4 = 8, 5 = 4, 6+ = 0
      self.update_score_display(matrix_panel)
    # Ghost could be on a square with food / power pellet in which case pacman would get points for both
    if self.check_in_enemies_ghosts(x, y) != -1 and self.ghosts_active:
      self.score += 200
      self.update_score_display(matrix_panel, ate_ghost=True)

  def update_lives_display(self, matrix_panel, init=False):
    # display lives
    x_val = 63
    if init:
      for y_val in range(self.lives):
        matrix_panel.offset_canvas.SetPixel(x_val, y_val, *PacmanGame.LIVES_COLOR)
    else:
      y_val = self.lives - 1
      if self.lives != 0:
        # turn off the pixel for the life that was lost
        matrix_panel.offset_canvas.SetPixel(x_val, y_val, 0, 0, 0)
    matrix_panel.matrix.SwapOnVSync(matrix_panel.offset_canvas)

  def update_score_display(self, matrix_panel, ate_ghost=False):
    # 1 color, 20 dots of space to work with
    # 1 dot = 20 points (if score < 400 points)
    # 1 dot = 200 points (if 400 <= score < 4000 points)
    # 1 dot = 2000 points (if 4000 <= score < 40000 points)
    # pattern continues
    x_val = 63
    dots_allocated_for_score_info = 20
    points_per_dot = 20
    while self.score > points_per_dot*dots_allocated_for_score_info:
      points_per_dot *= 10
    for i in range(dots_allocated_for_score_info):
      y_val = 31 - i
      matrix_panel.offset_canvas.SetPixel(x_val, y_val, 0, 0, 0)
    for i in range(self.score // points_per_dot):
      y_val = 31 - i
      matrix_panel.offset_canvas.SetPixel(x_val, y_val, *PacmanGame.SCORE_COLOR)

    matrix_panel.matrix.SwapOnVSync(matrix_panel.offset_canvas)

  def display_final_score(self, matrix_panel):
    # Just use draw text to display final score and level
    matrix_panel.offset_canvas.Clear()
    run_text = RunText(f"Game over! Score: {self.score}")
    run_text.process()

  class SearchNode():
    def __init__(self, coord, parent_coords = []):
      self.coord = coord
      self.f = 0
      self.g = 0
      self.parent_coords = parent_coords

  def move_enemies(self, matrix_panel):
    for (enemy_idx, coords), enemy_color in zip(self.enemies.items(), PacmanGame.ENEMY_COLORS):
      x_old, y_old = coords[0] # will be 1 timestep back if a change is made here
      x_old_2, y_old_2 = coords[1] # will be 2 timesteps back if a change is made here

      # if switch direction, just go back to the last tile that you were at
      #if self.switch_direction:
      #  x, y = x_old_2, y_old_2

      # First figure out the next best position for this enemy to move
      # Two modes: follow player, ambush player 
      # Make sure ghosts don't collide with walls, each other; collision with pacman?

      # if statements to determine timings for scatter mode, chase mode and then also movement according to those modes

      #if ghost in scatter mode then call enemy_scatter
      if self.scatter_timer[enemy_idx] >= 0:
        self.scatter_timer[enemy_idx] -= 1

      if self.scatter_timer[enemy_idx] > 0:
        x, y = self.enemy_scatter(enemy_idx, (x_old, y_old), (x_old_2, y_old_2))
      else:
        x, y = self.enemy_chase(enemy_idx, (x_old, y_old), (x_old_2, y_old_2))

      # after a movement has been decided, update self.enemies
      self.enemies[enemy_idx] = [(x, y), (x_old, y_old)]

      # TODO: Check whether this new position is the position of the pacman
      # need to check this here in case pacman is NOT moving and enemy caught up with pacman

      # set the color of the old square to what it was before the ghost was there
      matrix_panel.offset_canvas.SetPixel(x, y, *enemy_color)
      if (x_old, y_old) in self.food:
        matrix_panel.offset_canvas.SetPixel(x_old, y_old, *PacmanGame.FOOD_COLOR)
      elif (x_old, y_old) in self.power_pellets:
        matrix_panel.offset_canvas.SetPixel(x_old, y_old, *PacmanGame.POWER_PELLETS_COLOR)
      else:
        matrix_panel.offset_canvas.SetPixel(x_old, y_old, 0, 0, 0)
      matrix_panel.matrix.SwapOnVSync(matrix_panel.offset_canvas)

  def enemy_scatter(self, enemy_idx, old_pos, old_2_pos):
    # the enemy is scattering itself around the board
    #scatter_out_of_bounds_coords = [(-5, -5), (69, 5), (-5, 37), (69, 37)]
    scatter_coords = [(2, 2), (61, 2), (2, 31), (61, 31)]
    return self.update_enemy_pos(old_pos, old_2_pos, scatter_coords[enemy_idx])

  def enemy_chase(self, enemy_idx, old_pos, old_2_pos):
    return self.update_enemy_pos(old_pos, old_2_pos, self.pacman)
   
  def update_enemy_pos(self, old_pos, old_2_pos, target_pos):
    x_old, y_old = old_pos
    x_old_2, y_old_2 = old_2_pos
    # get all the possible coordinates the enemy can move to

    # in that list, if length of list > 1, remove the option to return to the square from which they came
    # if there are still multiple options, then randomly select one and move else just move to the option that is left
    possible_coords = self.get_possible_coordinates(x_old, y_old)
    if len(possible_coords) > 1 and (x_old_2, y_old_2) in possible_coords: # always want "forward" movement
      possible_coords.remove((x_old_2, y_old_2))
    if len(possible_coords) == 0:
      print("WARNING: No possible coordinates for the enemy to move.")
      x, y = x_old_2, y_old_2
    elif len(possible_coords) == 1:
      # No need to run the algorithm if there is one position you can go
      x, y = possible_coords[0]
    else:
      # have multiple choices, pick the best choice based on...
      # euclidean distance? dfs? bfs? a*
      # take into account: target coordinate (pacman position or out of bounds scatter position), 
      # distances to food clumps, other enemy positions, path
      #x, y = self.bfs((x_old, y_old), target_pos)
      
      distances = {}
      for x_poss, y_poss in possible_coords:
        dist = math.sqrt((x_poss-target_pos[0])**2 + (y_poss-target_pos[1])**2)
        distances[dist] = (x_poss, y_poss)
      x, y = distances[min(list(distances.keys()))]

    return x, y

  def bfs(self, ghost_pos, target_pos):
    closed = set() # like "visited" set
    open = [] # the active queue for positions to explore
    open.append(PacmanGame.SearchNode(ghost_pos))
    goal_node = PacmanGame.SearchNode(target_pos)

    while len(open) > 0:
      index = 0
      expanding_node = open[0]
      for i in range(len(open)):
        if expanding_node.f > open[i].f:
          expanding_node = open[i]
          index = i
      
      closed.add(open.pop(index).coord)

      if expanding_node.coord == goal_node.coord:
        goal_node = expanding_node
        # the shortest path to goal node is guaranteed by bfs
        return goal_node.parent_coords[0]

      expanding_node_x, expanding_node_y = expanding_node.coord

      possible_coords = self.get_possible_coordinates(expanding_node_x, expanding_node_y)
      possible_coords = [PacmanGame.SearchNode(c, expanding_node.parent_coords + [expanding_node.coord]) for c in possible_coords if c not in closed]

      # the coordinates that remain are viable candidates for expansion
      for search_node in possible_coords:
        search_node.g = expanding_node.g + 1
        search_node.f = search_node.g
        open.append(search_node)

    print("BFS did not work, picking randomly")
    possible_coords = self.get_possible_coordinates(*ghost_pos)
    return random.choice(possible_coords) if len(possible_coords) > 0 else ghost_pos

  def move_ghosts(self, matrix_panel):
    # No specific target tile, pseudorandomly decide which turns to make at every intersection
    for (ghost_idx, coords), ghost_color in zip(self.enemies.items(), PacmanGame.GHOST_COLORS):
      x_old, y_old = coords[0] # will be 1 timestep back if a change is made here
      x_old_2, y_old_2 = coords[1] # will be 2 timesteps back if a change is made here
      
      # first if they are in jail, do nothing
      if self.check_in_jail(x_old, y_old):
        continue

      # if switch direction, just go back to the last tile that you were at
      if self.switch_direction:
        x, y = x_old_2, y_old_2
      else:
        # else get a list of possible coordinates that they can move to
        # in that list, if length of list > 1, remove the option to return to the square from which they came
        # if there are still multiple options, then randomly select one and move else just move to the option that is left
        possible_coords = self.get_possible_coordinates(x_old, y_old)
        if len(possible_coords) > 1 and (x_old, y_old) in possible_coords: # always want "forward" movement
          possible_coords.remove((x_old, y_old))
        if len(possible_coords) == 0:
          print("WARNING: No possible coordinates for the ghost to move.")
          x, y = x_old, y_old
        else:
          x, y = random.choice(possible_coords)

      # after a movement has been decided update self.enemies and 
      # set the color of the old square to what it was before the ghost was there
      self.enemies[ghost_idx] = [(x, y), (x_old, y_old)]
      matrix_panel.offset_canvas.SetPixel(x, y, *ghost_color)
      if (x_old, y_old) in self.food:
        matrix_panel.offset_canvas.SetPixel(x_old, y_old, *PacmanGame.FOOD_COLOR)
      elif (x_old, y_old) in self.power_pellets:
        matrix_panel.offset_canvas.SetPixel(x_old, y_old, *PacmanGame.POWER_PELLETS_COLOR)
      else:
        matrix_panel.offset_canvas.SetPixel(x_old, y_old, 0, 0, 0)
      matrix_panel.matrix.SwapOnVSync(matrix_panel.offset_canvas)

  def free_ghosts_from_jail(self, matrix_panel):
    # TODO: check these starting coordinates
    starting_coords = [[(13, 30), (13, 30)], [(13, 33), (13, 33)], [(21, 29), (21, 29)], [(21, 34), (21, 34)]]
    for (enemy_idx, coords), enemy_color in zip(self.enemies.items(), PacmanGame.ENEMY_COLORS):
      x_old, y_old = coords[0] # possible position inside jail
      x, y = starting_coords[enemy_idx][0] # position outside jail

      if self.check_in_jail(x_old, y_old): # TODO TEST this
        # if it was in jail, free from jail and set the pixels
        self.enemies[enemy_idx] = starting_coords[enemy_idx]
        matrix_panel.offset_canvas.SetPixel(x, y, *enemy_color)
        matrix_panel.offset_canvas.SetPixel(x_old, y_old, 0, 0, 0)
      else:
        # dont remove from jail if never in jail
        # simply turn its color back from ghost to enemy
        matrix_panel.offset_canvas.SetPixel(x_old, y_old, *enemy_color)

    matrix_panel.matrix.SwapOnVSync(matrix_panel.offset_canvas)

  def check_in_jail(self, x, y):
    return (x, y) in self.jail.keys()

  def check_in_enemies_ghosts(self, x, y):
    for enemy_idx, coords in self.enemies.items():
      if x == coords[0][0] and y == coords[0][1]:
        return enemy_idx
    return -1

  def get_possible_coordinates(self, x_old, y_old):
    # For use by the ghost or enemy
    possible_coords = [(x_old-1, y_old), (x_old+1, y_old), (x_old, y_old-1), (x_old, y_old+1)]
    final_possible_coords = []
    for c in possible_coords:
      if c not in self.walls and not self.check_in_jail(*c): # not wall, jail
        final_possible_coords.append(c)
    return final_possible_coords
  
if __name__ == "__main__":  
  mpu_queue = Queue()
  volume_queue = Queue()

  i2c = board.I2C()  # uses board.SCL and board.SDA
  mpu = adafruit_mpu6050.MPU6050(i2c)
  mpu_thread = threading.Thread(target=pacman_sensors.read_pitch_roll, args=(mpu, mpu_queue,))
  mpu_thread.start()

  volume_thread = threading.Thread(target=pacman_sensors.read_volume, args=(volume_queue,))
  volume_thread.start()

  matrix_panel = MatrixPanel(mpu_queue, volume_queue)
  matrix_panel_thread = threading.Thread(target=matrix_panel.process, args=())
  matrix_panel_thread.start()

  #if (not matrix_panel.process()):
  #  matrix_panel.print_help()