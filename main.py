import pygame
import sys
import random

from game import *

import json
import numpy as np

with open("checkpoints.json", "r") as file:
    checkpoints = json.load(file)

pygame.init()
clock = pygame.time.Clock()
FPS = 60
running = True

playerCar = Car(64, checkpoints)
cars = [Car(27, checkpoints, color=RED), Car(28, checkpoints, color=GREEN)]

while running:
    screen.fill(BLACK)
    screen.blit(path_img, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if pygame.key.get_pressed()[pygame.K_r]:
        playerCar.reset()

    keys = pygame.key.get_pressed()
    turn = -1 if keys[pygame.K_a] else 1 if keys[pygame.K_d] else 0
    accel = -1 if keys[pygame.K_s] else 1 if keys[pygame.K_w] else 0
    playerCar.update(turn, accel)

    for car in cars:
        car.update(random.randint(-1, 1), random.randint(-1, 1))

    #write player current score in the top left
    font = pygame.font.Font(None, 36)
    message_top = f"Current Lap Time {playerCar.lap_time/FPS:.3f} | Score: {playerCar.checkpoints_reached} | Race Time: {playerCar.time_alive/FPS:.1f}"
    text_top = font.render(message_top, True, BLUE)
    screen.blit(text_top, (10, 10))
    message_bottom = f"Last Lap Time: {playerCar.last_lap_time/FPS:.3f} | Max Score: {playerCar.max_score} | Best Lap Time: {playerCar.min_lap_time/FPS:.3f}"
    text_bottom = font.render(message_bottom, True, BLUE)
    screen.blit(text_bottom, (10, 50))

    # Update display
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
