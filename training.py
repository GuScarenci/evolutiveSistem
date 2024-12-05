import pygame
import sys
import random
import json
import numpy as np
from game import *
from perceptron import Perceptron

# Load checkpoints
with open("checkpoints.json", "r") as file:
    checkpoints = json.load(file)

pygame.init()
clock = pygame.time.Clock()
FPS = 60

# Genetic algorithm parameters
POPULATION_SIZE = 10
MUTATION_RATE = 0.1
GENERATIONS = 100

# Initialize game
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Top-View Race Game with AI")
running = True

# Create the initial population of Perceptrons and cars
population = [
    {
        "perceptron": Perceptron(input_size=6, hidden_size=6, output_size=2),
        "car": Car(random.randint(1, len(checkpoints)), checkpoints, color=random.choice([RED, GREEN, BLUE]))
    }
    for _ in range(POPULATION_SIZE)
]

generation = 1

def evaluate_population():
    """Evaluate the fitness of each car in the population."""
    for individual in population:
        car = individual["car"]
        perceptron = individual["perceptron"]
        if car.running:
            inputs = np.array(car.ray_distances)
            if inputs.max() <= 0:
                inputs = np.ones_like(inputs) * -1
            turn, accel = perceptron.forward(inputs)
            car.update(turn=int(np.sign(turn)), accel=int(np.sign(accel)))

def create_next_generation():
    """Create the next generation by selecting, crossing over, and mutating perceptrons."""
    # Sort population by fitness (descending)
    population.sort(key=lambda ind: ind["car"].fitness, reverse=True)
    
    # Keep the top half as parents
    parents = population[:POPULATION_SIZE // 2]
    
    # Create new population through crossover and mutation
    new_population = []
    for i in range(POPULATION_SIZE):
        parent1 = random.choice(parents)["perceptron"]
        parent2 = random.choice(parents)["perceptron"]
        child_perceptron = Perceptron.crossover(parent1, parent2)
        child_perceptron.mutate(MUTATION_RATE)
        new_population.append({
            "perceptron": child_perceptron,
            "car": Car(random.randint(1, len(checkpoints)), checkpoints, color=random.choice([RED, GREEN, BLUE]))
        })
    
    return new_population

previous_generation_best_fitness = 0
best_fitness = 0

while running:
    screen.fill(BLACK)
    screen.blit(path_img, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Evaluate the population
    evaluate_population()
    
    # Check if all cars have stopped running
    if all(not individual["car"].running for individual in population):
        generation += 1
        if generation > GENERATIONS:
            running = False
            continue
        previous_generation_best_fitness = max(individual["car"].fitness for individual in population)
        best_fitness = max(best_fitness, previous_generation_best_fitness)

        population = create_next_generation()

    # Render cars and display stats
    for individual in population:
        individual["car"].draw()

    font = pygame.font.Font(None, 36)
    message = f"Generation: {generation} | Previous best fitness: {previous_generation_best_fitness:.0f} | Best fitness Overall: {best_fitness:.0f}"
    text = font.render(message, True, WHITE)
    screen.blit(text, (10, 10))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()

