import pygame
import sys
import random
import json
import numpy as np
from game import *
from perceptron import Perceptron

# Genetic Algorithm HYPERPARAMETERS
POPULATION_SIZE = 50
MUTATION_RATE = 0.25
MUTATION_MODULUS = 1
GENERATIONS = 1000
BREEDING_NUM = 5
TOP_SCORES_TO_CONSERVE = 35
BREED_EVERY = 3
HIDDEN_LAYER_SIZE = 8
CHECKPOINT = 102

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
        "car": Car(CHECKPOINT, checkpoints, color=random.choice([RED, GREEN, BLUE]))
    }
    for _ in range(POPULATION_SIZE)
]

previous_population = [
        {
            "perceptron": individual["perceptron"].copy(),
            "car": individual["car"].copy()
        }
        for individual in population
    ]

generation = 1

goldPerceptron = Perceptron(input_size=6, hidden_size=6, output_size=2)
goldPerceptron.load_perceptron("safe_perceptron.npz")

population[0]["perceptron"] = goldPerceptron

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
    for i in range(len(population)):
        if population[i]["car"].fitness < previous_population[i]["car"].fitness:
            population[i] = previous_population[i]
        else:
            previous_population[i] = population[i]

        population[i]['perceptron'].mutate(MUTATION_RATE, MUTATION_MODULUS)

def breed_population():
    """Make the best individual the parent of all others and create the next generation."""
    global population, generations_since_new_best
    gene_pool = population + previous_population
    gene_pool.sort(key=lambda ind: ind["car"].fitness, reverse=True)
    
    # Find the best individual (highest fitness)
    best_individual = gene_pool[0]
    gene_pool = gene_pool[1: POPULATION_SIZE]
    best_perceptron = best_individual["perceptron"]
    
    # Create new population with the best individual as parent
    new_population = []
    
    # Keep the best individual as-is (no crossover or mutation)
    new_population.append({
        "perceptron": best_perceptron.copy(),
        "car": Car(CHECKPOINT, checkpoints, color=random.choice([RED, BLUE]))
    })

    # Create the rest of the population by crossing over the best individual with others
    for individual in gene_pool: 
        # Perform crossover between the best individual and the random individual
        child_perceptron = Perceptron.crossover(best_perceptron, individual['perceptron'])

        if generations_since_new_best > 5:
            child_perceptron = Perceptron(input_size=6, hidden_size=HIDDEN_LAYER_SIZE, output_size=2)
        
        # Optionally, you can mutate the child perceptron to maintain genetic diversity
        child_perceptron.mutate(MUTATION_RATE / 5, MUTATION_MODULUS / 2)
        
        # Add the child to the new population
        new_population.append({
            "perceptron": child_perceptron,
            "car": Car(CHECKPOINT, checkpoints, color=random.choice([RED, BLUE]))
        })

    if generations_since_new_best > 9:
        print("DECIMATED")
        generations_since_new_best = 0

    population = new_population

previous_generation_best_fitness = 0
best_fitness = 0
generations_since_new_best = 0

while running:
    screen.fill(BLACK)
    screen.blit(path_img, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_s]:
        #get best perceptron from population
        best_perceptron = max(population, key=lambda ind: ind["car"].fitness)["perceptron"]
        file_name = f"perceptron_{generation}.json"
        best_perceptron.save_perceptron(file_name)
        print(f"Best perceptron saved to {file_name}")

    # Evaluate the population
    evaluate_population()
    
    # Check if all cars have stopped running
    if all(not individual["car"].running for individual in population):
        previous_generation_best_fitness = max(individual["car"].fitness for individual in population)
        best_fitness = max(best_fitness, previous_generation_best_fitness)
        generations_since_new_best += 1
        
        if previous_generation_best_fitness == best_fitness:
            generations_since_new_best = 0
        if generation % BREED_EVERY == 0:
            breed_population()
        else:
            mutate_population()

        generation += 1
        if generation > GENERATIONS:
            running = False
            continue

        # Reset cars for the new generation
        for individual in population:
            individual["car"].reset()

    # Render cars and display stats
    for individual in population:
        individual["car"].draw()

    font = pygame.font.Font(None, 36)
    message = f"Generation: {generation} | Previous best fitness: {previous_generation_best_fitness:.0f} | Best fitness Overall: {best_fitness:.0f} | Generations since new best: {generations_since_new_best}"
    text = font.render(message, True, WHITE)
    screen.blit(text, (10, 10))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
