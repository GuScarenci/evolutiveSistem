import pygame
import sys
import random
import json
import numpy as np
from game import *
from perceptron import Perceptron

# Genetic Algorithm HYPERPARAMETERS
POPULATION_SIZE = 50
MUTATION_RATE = 0.1
MUTATION_MODULUS = 0.5
GENERATIONS = 1000
BREEDING_NUM = 5
TOP_SCORES_TO_CONSERVE = 35
BREED_EVERY = 5
HIDDEN_LAYER_SIZE = 6

# Load checkpoints
with open("checkpoints.json", "r") as file:
    checkpoints = json.load(file)

pygame.init()
clock = pygame.time.Clock()
FPS = 60

# Initialize game
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Top-View Race Game with AI")
running = True

# Create the initial population of Perceptrons and cars
population = [
    {
        "perceptron": Perceptron(input_size=6, hidden_size=HIDDEN_LAYER_SIZE, output_size=2),
        "car": Car(None, checkpoints, color=random.choice([RED, GREEN, BLUE]))
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

def mutate_population():
    """Mutate the population and rollback if fitness decreases."""
    global population
    previous_population = [
        {
            "perceptron": individual["perceptron"].copy(),
            "car": individual["car"].copy()
        }
        for individual in population
    ]
    for individual in population:
        individual["perceptron"].mutate(MUTATION_RATE, MUTATION_MODULUS)

    # Reevaluate fitness after mutation
    evaluate_population()

    # Rollback if fitness is worse
    for i in range(len(population)):
        if population[i]["car"].fitness < previous_population[i]["car"].fitness:
            population[i] = previous_population[i]

def breed_population():
    """Select the top 5 fittest individuals and create the next generation."""
    global population
    # Sort population by fitness (descending)
    population.sort(key=lambda ind: ind["car"].fitness, reverse=True)

    # Select the top 5 fittest
    top_fittest = population[:TOP_SCORES_TO_CONSERVE]

    # Create new population
    new_population = []

    # Keep the top 5
    new_population.extend(top_fittest)

    # Create 10 pairwise crossovers between the top 5
    for i in range(BREEDING_NUM):
        for j in range(i + 1, BREEDING_NUM):
            parent1 = top_fittest[i]["perceptron"]
            parent2 = top_fittest[j]["perceptron"]
            child_perceptron = Perceptron.crossover(parent1, parent2)
            child_perceptron.mutate(MUTATION_RATE, MUTATION_MODULUS)
            new_population.append({
                "perceptron": child_perceptron,
                "car": Car(None, checkpoints, color=random.choice([RED, GREEN, BLUE]))
            })

    # Add 5 new random individuals
    while len(new_population) < POPULATION_SIZE:
        new_population.append({
            "perceptron": Perceptron(input_size=6, hidden_size=HIDDEN_LAYER_SIZE, output_size=2),
            "car": Car(None, checkpoints, color=random.choice([RED, GREEN, BLUE]))
        })

    population = new_population

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

        if generation % BREED_EVERY == 0:
            breed_population()
        else:
            mutate_population()

        generation += 1
        if generation > GENERATIONS:
            running = False
            continue

        previous_generation_best_fitness = max(individual["car"].fitness for individual in population)
        best_fitness = max(best_fitness, previous_generation_best_fitness)


        # Reset cars for the new generation
        for individual in population:
            individual["car"].reset()

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
