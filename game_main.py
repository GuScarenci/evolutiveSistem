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

playerCar = Car(102, checkpoints, training_mode=False)
aiCar = Car(102, checkpoints, color=RED, training_mode=False)
aiPerceptron = Perceptron(input_size=6, hidden_size=6, output_size=2)
aiPerceptron.load_perceptron("safe_perceptron.npz")

cars = [playerCar, aiCar]

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

    inputs = np.array(aiCar.ray_distances)
    if inputs.max() <= 0:
        inputs = np.ones_like(inputs) * -1
    turn, accel = aiPerceptron.forward(inputs)
    aiCar.update(turn=int(np.sign(turn)), accel=int(np.sign(accel)))

    anchor = 0
    for car in cars:
        font = pygame.font.Font(None, 36)
        message_top = f"Lap Time {car.lap_time/FPS:.3f} | Race Time: {car.time_alive/FPS:.1f} | Lap: {car.lap_count}"
        message_bottom = f"Last Lap Time: {car.last_lap_time/FPS:.3f} | Best Lap Time: {car.min_lap_time/FPS:.3f}"
        text_top = font.render(message_top, True, car.color)
        text_bottom = font.render(message_bottom, True, car.color)
        screen.blit(text_top, (10  + 1000*anchor, 10))
        screen.blit(text_bottom, (10 + 1000*anchor, 50))
        anchor += 1

    # Update display
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
