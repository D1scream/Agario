
import math
import random
WINDOW_WIDTH, WINDOW_HEIGHT = 1600, 900
FIELD_WIDTH, FIELD_HEIGHT = 1600, 900
MASS_FOR_EAT_PLAYER = 0.8
TICK_INTERVAL = 1 / 60



def generate_random_color(min_sum=0, max_sum=600):
            while True:
                color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                if sum(color) <= max_sum and sum(color) >= min_sum:
                    return color