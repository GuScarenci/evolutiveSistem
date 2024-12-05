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

playerCar = Car(102, checkpoints)
aiCar = Car(102, checkpoints, color=RED)
aiPerceptron = Perceptron(input_size=6, hidden_size=6, output_size=2)
aiPerceptron.load_perceptron("best_perceptron.json.npz")

while running:
    #hardcoded way to keep it always running
    aiCar.running = True
    playerCar.running = True

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
