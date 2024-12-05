import pygame
import sys
import math
import numpy as np
import random

from game import *

import json
import cv2
import numpy as np

# Function to load the checkpoint data from the JSON file
def load_checkpoints(json_file_path):
    with open(json_file_path, "r") as file:
        checkpoints = json.load(file)
    return checkpoints

# Function to check if a point is inside a checkpoint rectangle
def is_point_inside_checkpoint(checkpoints, checkpoint_number, point):
    """
    Verifies if a given point is inside the rectangle of a specific checkpoint.

    Args:
        checkpoints (list): List of checkpoint data loaded from the JSON.
        checkpoint_number (int): The ID of the checkpoint to check.
        point (tuple): The point (x, y) to check.

    Returns:
        bool: True if the point is inside the rectangle, False otherwise.
    """
    # Find the specified checkpoint
    for checkpoint in checkpoints:
        if checkpoint["id"] == checkpoint_number:
            rectangle = checkpoint["rectangle"]

            # Convert the rectangle points to a numpy array
            rect_points = np.array(rectangle, dtype=np.int32)

            # Use cv2.pointPolygonTest to check if the point is inside
            inside = cv2.pointPolygonTest(rect_points, point, False)

            return inside >= 0  # Returns True if point is inside or on the edge

    # If checkpoint number is not found, raise an error
    raise ValueError(f"Checkpoint {checkpoint_number} not found in the JSON file.")

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
