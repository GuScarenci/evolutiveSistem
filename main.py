import pygame
import sys
import math
import numpy as np
import random

from game import *

# Initialize Pygame
pygame.init()

# Main game loop
running = True
reset_ai_car()

while running:
    screen.fill(BLACK)
    screen.blit(path_img, (0, 0))

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update AI car
    car_rect = update_ai_car()

    # Check if AI car dies
    if not is_car_on_path([
        car_rect.topleft, car_rect.topright, car_rect.bottomleft, car_rect.bottomright
    ]):
        scores[current_ai] = time_alive
        current_ai += 1
        if current_ai >= POPULATION_SIZE:
            evolve_population()
            current_ai = 0
        reset_ai_car()

    # Update score for current AI
    time_alive += 1

    # Update display
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
