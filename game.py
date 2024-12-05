import pygame
import math
import numpy as np
import cv2
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

path_img = pygame.image.load("track.png")  # Replace with your path image
path_img = pygame.transform.scale(path_img, (WIDTH, HEIGHT))  # Scale to fit screen
car_img  = pygame.image.load("car.png")
car_img  = pygame.transform.scale(car_img, (30, 30))


class Car:
    def __init__(self, checkpoint_, checkpoints, angle=90, 
                 speed=0, car_img=car_img, color=BLUE):
        self.start_checkpoint = checkpoint_ - 1 if checkpoint_ is not None else None
        self.checkpoints = checkpoints
        self.start_angle = angle
        self.start_speed = speed
        self.color = color
        self.image = car_img

        self.rotation_speed = 2
        self.max_speed = 5
        self.acceleration = 0.05
        self.deceleration = 0.1
        self.hitbox = (25, 20)
        self.max_ray_length = 300
        self.max_frames_to_reach_checkpoint = 60
        self.ray_angles = [-90, -45, 0, 45, 90, 180]

        self.max_score = 0
        self.min_lap_time = 0
        self.last_lap_time = 0

        self.reset()

    def reset(self):
        start_checkpoint = self.start_checkpoint if self.start_checkpoint is not None else random.randint(0, len(self.checkpoints) - 1)
        checkpoint = self.checkpoints[start_checkpoint]["rectangle"]
        self.x = sum(x for x, y in checkpoint) / 4
        self.y = sum(y for x, y in checkpoint) / 4
        self.angle = self.start_angle
        self.speed = self.start_speed
        self.next_checkpoint = start_checkpoint + 1
        self.rect = self.image.get_rect(center=(self.x, self.y))

        self.fitness = 0
        self.time_alive = 0
        self.checkpoints_reached = 0
        self.lap_time = 0
        self.frames_since_last_checkpoint = 0
        self.ray_distances = [0] * len(self.ray_angles)

        self.running = True

    def die(self):
        self.running = False
        self.max_score = max(self.max_score, self.checkpoints_reached)

    def update(self, turn=0, accel=0):
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
                self.speed = max(self.speed - self.acceleration * 0.2, -self.max_speed / 2)
        else:
            self.speed *= 0.99  # Natural deceleration

        # Update position
        self.x -= self.speed * math.sin(math.radians(self.angle))
        self.y -= self.speed * math.cos(math.radians(self.angle))

        # Update rectangle position
        self.draw()
        self.cast_rays()

        self.is_on_checkpoint()

        self.frames_since_last_checkpoint += 1
        self.time_alive += 1
        self.lap_time += 1

        self.fitness = self.checkpoints_reached * 500 + self.time_alive/10

        timeout = self.frames_since_last_checkpoint > self.max_frames_to_reach_checkpoint
        if not self.is_on_path() or timeout:
            self.die()

    def draw(self):
        custom_hitbox = pygame.Rect(0, 0, self.hitbox[0], self.hitbox[1])
        custom_hitbox.center = self.rect.center
        pygame.draw.rect(screen, self.color, custom_hitbox, 2)

        rotated_car = pygame.transform.rotate(self.image, self.angle)
        self.rect = rotated_car.get_rect(center=(self.x, self.y))
        screen.blit(rotated_car, self.rect.topleft)

        # write fitness score next to the car
        font = pygame.font.Font(None, 36)
        message = f"{self.fitness:.0f}"
        text = font.render(message, True, BLACK)
        screen.blit(text, (self.x, self.y))


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

    def is_on_checkpoint(self):
        points = [self.rect.topleft, self.rect.topright, self.rect.bottomleft, self.rect.bottomright]

        for point in points:
            if self.next_checkpoint == len(self.checkpoints):
                self.next_checkpoint = 0
            rectangle = self.checkpoints[self.next_checkpoint]["rectangle"]
            rect_points = np.array(rectangle, dtype=np.int32)
            inside = cv2.pointPolygonTest(rect_points, point, False)

            if inside >= 0:
                if self.next_checkpoint == self.start_checkpoint:
                    self.min_lap_time = min(self.min_lap_time, self.lap_time) if self.min_lap_time != 0 else self.lap_time
                    self.last_lap_time = self.lap_time
                    self.lap_time = 0
                self.frames_since_last_checkpoint = 0
                self.checkpoints_reached += 1
                self.next_checkpoint += 1
                if self.next_checkpoint == len(self.checkpoints):
                    self.next_checkpoint = 0

                pygame.draw.polygon(screen, self.color, rect_points, 15)

    def cast_rays(self):
        self.ray_distances = []
        for angle_offset in self.ray_angles:
            ray_angle = self.angle + angle_offset
            distance = 0
            while distance < self.max_ray_length:
                ray_x = self.x - distance * math.sin(math.radians(ray_angle))
                ray_y = self.y - distance * math.cos(math.radians(ray_angle))

                if not (0 <= ray_x < WIDTH and 0 <= ray_y < HEIGHT):
                    break

                if path_img.get_at((int(ray_x), int(ray_y))) != WHITE:
                    break

                distance += 1

            if distance == self.max_ray_length:
                distance = -1

            self.ray_distances.append(distance)
            pygame.draw.line(screen, self.color, (self.x, self.y), (ray_x, ray_y), 1)

    def copy(self):
        """
        Creates a deep copy of the Car instance.
        """
        new_car = Car(
            checkpoint_=self.start_checkpoint,
            checkpoints=self.checkpoints,
            angle=self.start_angle,
            speed=self.start_speed,
            car_img=self.image,  # Use the existing car image
            color=self.color
        )

        new_car.x = self.x
        new_car.y = self.y
        new_car.angle = self.angle
        new_car.speed = self.speed
        new_car.next_checkpoint = self.next_checkpoint
        new_car.fitness = self.fitness
        new_car.time_alive = self.time_alive
        new_car.checkpoints_reached = self.checkpoints_reached
        new_car.lap_time = self.lap_time
        new_car.frames_since_last_checkpoint = self.frames_since_last_checkpoint
        new_car.ray_distances = self.ray_distances[:]
        new_car.running = self.running
        new_car.max_score = self.max_score
        new_car.min_lap_time = self.min_lap_time
        new_car.last_lap_time = self.last_lap_time

        new_car.rect = self.rect.copy()

        return new_car
