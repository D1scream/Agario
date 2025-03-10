
import math
WIDTH, HEIGHT = 1280, 720
MASS_FOR_EAT_PLAYER = 0.8

def score_to_speed(score):
    return 20 / math.log(score, 2)
