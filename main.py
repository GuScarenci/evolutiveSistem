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

# Initialize Pygame
pygame.init()

# Main game loop
running = True
reset_ai_car()

json_file_path = "checkpoints.json"  # Replace with your JSON file path
checkpoints = load_checkpoints(json_file_path)
current_checkpoint = 8
checkpoints_reached = 0

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
        scores[current_ai] = checkpoints_reached/time_alive + time_alive
        current_ai += 1
        if current_ai >= POPULATION_SIZE:
            evolve_population()
            current_ai = 0
        current_checkpoint = 8
        checkpoints_reached = 0
        reset_ai_car()

    car_inside_checkpoint = is_point_inside_checkpoint(checkpoints, current_checkpoint, car_rect.topleft) or is_point_inside_checkpoint(checkpoints, current_checkpoint, car_rect.topright) or is_point_inside_checkpoint(checkpoints, current_checkpoint, car_rect.bottomleft) or is_point_inside_checkpoint(checkpoints, current_checkpoint, car_rect.bottomright)

    if car_inside_checkpoint:
        print(f"AI car reached checkpoint {current_checkpoint}")
        checkpoints_reached += 1
        current_checkpoint += 1
        if current_checkpoint > len(checkpoints):
            current_checkpoint = 1

    # Update score for current AI
    time_alive += 1

    # Update display
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
