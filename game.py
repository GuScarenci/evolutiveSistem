import pygame
import sys
import math
import numpy as np
import random
from perceptron import *

# Screen dimensions
WIDTH, HEIGHT = 1920, 1080
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Top-View Race Game with AI")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

# Clock and FPS
clock = pygame.time.Clock()
FPS = 60

path_img = pygame.image.load("track.png")  # Replace with your path image
path_img = pygame.transform.scale(path_img, (WIDTH, HEIGHT))  # Scale to fit screen

class Car:
    def __init__(self, checkpoint_, checkpoints, angle=90, speed=0, car_img='car.png', color=BLUE):
        self.start_checkpoint = checkpoint_ -1
        checkpoint = checkpoints[self.start_checkpoint]["rectangle"]
        self.start_X = sum(x for x, y in checkpoint) / 4
        self.start_Y = sum(y for x, y in checkpoint) / 4
        self.checkpoints = checkpoints
        self.start_angle = angle
        self.start_speed = speed
        self.image = pygame.image.load(car_img)  # Replace with your car image

        self.rotation_speed = 2
        self.max_speed = 5
        self.acceleration = 0.05
        self.deceleration = 0.1
        self.hitbox = (25, 20)
        self.max_ray_length = 300
        self.ray_angles = [-90, -45, 0, 45, 90, 180]
        self.image = pygame.transform.scale(self.image, (30, 30))  # Resize car

        self.color = color

        self.reset()

    def reset(self):
        self.x = self.start_X
        self.y = self.start_Y
        self.angle = self.start_angle
        self.speed = self.start_speed
        self.next_checkpoint = self.start_checkpoint+1
        self.checkpoints_reached = 0
        self.max_frames_to_reach_checkpoint = 300
        self.frames_since_last_checkpoint = 0
        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.ray_distances = [0] * len(self.ray_angles)
        self.running = True

    def update(self, turn=0, accel=0):
        """
        Update the car's state.
        
        Args:
            turn (int): -1 for left, 1 for right, 0 for no turning.
            accel (int): 1 for acceleration, 0 for no acceleration, -1 for braking
        """
        if not self.running:
            self.draw()
            return

        # Handle turning
        if turn == -1:  # Turn left
            self.angle += self.rotation_speed
        elif turn == 1:  # Turn right
            self.angle -= self.rotation_speed

        # Handle acceleration and braking
        if accel == 1:  # Accelerate
            self.speed = min(self.speed + self.acceleration, self.max_speed)
        elif accel == -1:  # Brake
            if self.speed > 0:
                self.speed = max(self.speed - self.deceleration, -self.max_speed / 2)
            else:
                self.speed = max(self.speed - self.acceleration, -self.max_speed / 2)
        else:
            self.speed *= 0.99  # Natural deceleration

        # Update position
        self.x -= self.speed * math.sin(math.radians(self.angle))
        self.y -= self.speed * math.cos(math.radians(self.angle))

        # Update rectangle position
        self.draw()
        self.cast_rays()

        if not self.is_on_path():
            self.running = False


    def draw(self):
        custom_hitbox = pygame.Rect(0, 0, self.hitbox[0], self.hitbox[1])
        custom_hitbox.center = self.rect.center
        pygame.draw.rect(screen, self.color, custom_hitbox, 2)

        rotated_car = pygame.transform.rotate(self.image, self.angle)
        self.rect = rotated_car.get_rect(center=(self.x, self.y))
        screen.blit(rotated_car, self.rect.topleft)

    def is_on_path(self):
        points_to_check = [
            (self.x - self.hitbox[0] // 2, self.y - self.hitbox[1] // 2),
            (self.x + self.hitbox[0] // 2, self.y - self.hitbox[1] // 2),
            (self.x + self.hitbox[0] // 2, self.y + self.hitbox[1] // 2),
            (self.x - self.hitbox[0] // 2, self.y + self.hitbox[1] // 2)
        ]

        for point in points_to_check:
            if 0 <= point[0] < WIDTH and 0 <= point[1] < HEIGHT:
                if path_img.get_at((int(point[0]), int(point[1]))) != WHITE:
                    return False
        return True
    
    def cast_rays(self):
        """
        Casts rays in predefined directions and calculates the distance to the nearest non-white pixel.
        """
        self.ray_distances = []
        for angle_offset in self.ray_angles:
            ray_angle = self.angle + angle_offset
            distance = 0
            while distance < self.max_ray_length:
                # Calculate the position of the ray endpoint
                ray_x = self.x - distance * math.sin(math.radians(ray_angle))
                ray_y = self.y - distance * math.cos(math.radians(ray_angle))

                # Check if the ray is out of bounds
                if not (0 <= ray_x < WIDTH and 0 <= ray_y < HEIGHT):
                    break

                # Check if the pixel is off the track
                if path_img.get_at((int(ray_x), int(ray_y))) != WHITE:
                    break

                distance += 1
            
            if distance == self.max_ray_length:
                distance = -1

            self.ray_distances.append(distance)
            # Visualize the ray
            pygame.draw.line(screen, self.color, (self.x, self.y), (ray_x, ray_y), 1)
