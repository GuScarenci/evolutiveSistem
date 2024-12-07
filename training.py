import pygame
import sys
import time
import json
import numpy as np
from game import *
from perceptron import Perceptron

# Genetic Algorithm HYPERPARAMETERS
POPULATION_SIZE = 50
MUTATION_RATE = 0.1
MUTATION_MODULUS = 0.8
GENERATIONS = 1000
TOP_SCORES_TO_CONSERVE = 30
BREED_EVERY = 3
CHECKPOINT = 102
HIDDEN_LAYER_SIZE = 8
PERCEPTRON_INPUT_SIZE = 7
PERCEPTRON_OUTPUT_SIZE = 2

# Load checkpoints
with open("assets/checkpoints.json", "r") as file:
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
        "perceptron": Perceptron(input_size=PERCEPTRON_INPUT_SIZE, hidden_size=HIDDEN_LAYER_SIZE, output_size=2),
        "car": Car(CHECKPOINT, checkpoints, color=RED)
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

#goldPerceptron = Perceptron(input_size=PERCEPTRON_INPUT_SIZE, hidden_size=6, output_size=2)
#goldPerceptron.load_perceptron("safe_perceptron.npz")
#population[0]["perceptron"] = goldPerceptron

def evaluate_population():
    """Evaluate the fitness of each car in the population."""
    for individual in population:
        car = individual["car"]
        perceptron = individual["perceptron"]
        if car.running:
            normalized_speed = car.speed / car.max_speed
            inputs = np.array(car.ray_distances + [normalized_speed])
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
        population[i]['car'].reset()

def breed_population():
    """Make the best individual the parent of all others and create the next generation."""
    global population, breeds_since_new_best, best_individual
    best_perceptron = best_individual["perceptron"]

    gene_pool = population + previous_population
    gene_pool = sorted(gene_pool, key=lambda ind: ind["car"].fitness, reverse=True)
    gene_pool = gene_pool[:POPULATION_SIZE]

    new_population = []
    new_population.append({
        "perceptron": best_perceptron.copy(),
        "car": Car(CHECKPOINT, checkpoints, color=BLUE)
    })

    for i in range(TOP_SCORES_TO_CONSERVE):
        perceptron_to_conserve = gene_pool[i]["perceptron"]
        child_perceptron = Perceptron.crossover(best_perceptron, perceptron_to_conserve)
        child_perceptron.mutate(MUTATION_RATE, MUTATION_MODULUS)
        new_population.append({
            "perceptron": child_perceptron,
            "car": Car(CHECKPOINT, checkpoints, color=BLUE)
        })

    decimate_population = breeds_since_new_best > 3
    for _ in range(TOP_SCORES_TO_CONSERVE + 1, POPULATION_SIZE):
        if decimate_population:
            new_perceptron = Perceptron(input_size=PERCEPTRON_INPUT_SIZE, hidden_size=HIDDEN_LAYER_SIZE, output_size=2)
            child_perceptron = Perceptron.crossover(best_perceptron, new_perceptron)
            new_population.append({
                "perceptron": child_perceptron,
                "car": Car(CHECKPOINT, checkpoints, color=RED)
            })
        else:
            individual = gene_pool[i]
            child_perceptron = Perceptron.crossover(best_perceptron, individual['perceptron'])
            child_perceptron.mutate(MUTATION_RATE / 5, MUTATION_MODULUS / 2)
            new_population.append({
                "perceptron": child_perceptron,
                "car": Car(CHECKPOINT, checkpoints, color=BLUE)
            })

    population = new_population

generation_best = population[0]
ai_ghost = generation_best
best_individual = population[0]
breeds_since_new_best = 0

trackColored  = pygame.image.load("assets/trackColored.png")
trackColored  = pygame.transform.scale(trackColored, (1920, 1080))

while running:
    screen.fill(BLACK)
    screen.blit(trackColored, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_s]:
        best_perceptron = best_individual["perceptron"]
        lap_time = best_individual["car"].min_lap_time / FPS
        file_name = f"assets/models/perceptron_{lap_time:.3f}.json"
        best_perceptron.save_perceptron(file_name)
        print(f"Perceptron saved to {file_name}")

    # Evaluate the population
    evaluate_population()

    aiCar = ai_ghost["car"]
    aiNormalizedSpeed = aiCar.speed / aiCar.max_speed
    inputs = np.array(aiCar.ray_distances + [aiNormalizedSpeed])
    if inputs.max() <= 0:
        inputs = np.ones_like(inputs) * -1
    turn, accel = ai_ghost["perceptron"].forward(inputs)
    aiCar.update(turn=int(np.sign(turn)), accel=int(np.sign(accel)))

    #basically tests if one car has completed the required number of laps, if so the race can finish
    race_finished = False
    cars_finished = 0
    for individual in population:
        car = individual["car"]
        if not car.running:
            cars_finished += 1
            if car.lap_count >= car.max_laps_in_training:
                race_finished = True
                break
    race_finished = race_finished if cars_finished != len(population) else True
    
    if race_finished:
        generation_best_ = max(population, key=lambda ind: ind["car"].fitness)
        generation_best = {"perceptron": generation_best_["perceptron"].copy(), "car": generation_best_["car"].copy()}

        if generation_best["car"].fitness > best_individual["car"].fitness:
            best_individual = {"perceptron": generation_best["perceptron"].copy(), "car": generation_best["car"].copy()}

            ai_ghost = {"perceptron": best_individual["perceptron"].copy(), "car": best_individual["car"].copy()}
            ai_ghost["car"].color = GREEN

            breeds_since_new_best = 0

        ai_ghost["car"].reset()
        
        if generation % BREED_EVERY == 0:
            breeds_since_new_best += 1
            breed_population()
        else:
            mutate_population()

        generation += 1
        if generation > GENERATIONS:
            running = False
            continue

    # Render cars and display stats
    for individual in population:
        if not individual["car"].running:
            individual["car"].draw()

    font = pygame.font.Font(None, 36)
    message_top = f"Generation: {generation} | Best fitness Overall: {best_individual["car"].fitness:.0f} | Best Lap Time: {best_individual["car"].min_lap_time/FPS:.3f}"
    message_bottom = f"Previous best fitness: {generation_best["car"].fitness:.0f} | Best Lap Time: {generation_best["car"].min_lap_time/FPS:.3f} | Breeds since new best: {breeds_since_new_best}"

    text_top = font.render(message_top, True, GREEN)
    screen.blit(text_top, (10, 10))
    text_bottom = font.render(message_bottom, True, RED)
    screen.blit(text_bottom, (10, 50))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
