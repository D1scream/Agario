
import math
WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
FIELD_WIDTH, FIELD_HEIGHT = 1300, 800
MASS_FOR_EAT_PLAYER = 0.8

def score_to_speed(score):
    return 20 / math.log(score, 2)
