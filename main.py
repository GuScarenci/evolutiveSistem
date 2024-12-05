import pygame
import sys
import random

from game import *

import json
import numpy as np

# Function to load the checkpoint data from the JSON file
def load_checkpoints(json_file_path):
    with open(json_file_path, "r") as file:
        checkpoints = json.load(file)
    return checkpoints

json_file_path = "checkpoints.json"
checkpoints = load_checkpoints(json_file_path)
current_checkpoint = 27
checkpoints_reached = 0
max_frames_to_reach_checkpoint = 300
frames_since_last_checkpoint = 0

pygame.init()
running = True

playerCar = Car(64, checkpoints)
cars = [Car(27, checkpoints, color=RED), Car(28, checkpoints, color=GREEN)]

while running:
    screen.fill(BLACK)
    screen.blit(path_img, (0, 0))

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if pygame.key.get_pressed()[pygame.K_r]:
        playerCar.reset()

    keys = pygame.key.get_pressed()
    turn = -1 if keys[pygame.K_a] else 1 if keys[pygame.K_d] else 0
    accel = -1 if keys[pygame.K_s] else 1 if keys[pygame.K_w] else 0

    for car in cars:
        car.update(random.randint(-1, 1), random.randint(-1, 1))

    playerCar.update(turn, accel)
        
    # Update display
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
