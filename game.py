import pygame
import sys
import math
import numpy as np
import random

# Initialize Pygame
pygame.init()

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

# Load assets
car_img = pygame.image.load("car.png")  # Replace with your car image
car_img = pygame.transform.scale(car_img, (30, 30))  # Resize car
path_img = pygame.image.load("track.png")  # Replace with your path image
path_img = pygame.transform.scale(path_img, (WIDTH, HEIGHT))  # Scale to fit screen

# Neural Network Class
class NeuralNetwork:
    def __init__(self, input_size, hidden_size, output_size):
        # Initialize weights
        self.input_to_hidden = np.random.uniform(-1, 1, (input_size, hidden_size))
        self.hidden_to_output = np.random.uniform(-1, 1, (hidden_size, output_size))
        self.hidden_bias = np.zeros(hidden_size)
        self.output_bias = np.zeros(output_size)

    def forward(self, inputs):
        # Forward pass
        hidden_layer = np.tanh(np.dot(inputs, self.input_to_hidden) + self.hidden_bias)
        output_layer = np.tanh(np.dot(hidden_layer, self.hidden_to_output) + self.output_bias)
        return output_layer

# Genetic Algorithm functions
def crossover(parent1, parent2):
    child = NeuralNetwork(input_size=4, hidden_size=6, output_size=2)
    child.input_to_hidden = (parent1.input_to_hidden + parent2.input_to_hidden) / 2
    child.hidden_to_output = (parent1.hidden_to_output + parent2.hidden_to_output) / 2
    return child

def mutate(nn):
    for matrix in [nn.input_to_hidden, nn.hidden_to_output]:
        if random.random() < MUTATION_RATE:
            matrix += np.random.uniform(-0.1, 0.1, matrix.shape)

def evolve_population():
    global population, scores
    # Pair each neural network with its score
    scored_population = list(zip(scores, population))
    # Sort by score in descending order
    scored_population.sort(key=lambda pair: pair[0], reverse=True)
    # Extract the top half of the population (the best performing networks)
    survivors = [pair[1] for pair in scored_population[:POPULATION_SIZE // 2]]
    # Reproduce new population with mutations
    new_population = []
    for _ in range(POPULATION_SIZE):
        parent1, parent2 = random.choices(survivors, k=2)  # Select two parents
        child = crossover(parent1, parent2)  # Combine parents' weights
        mutate(child)  # Mutate child
        new_population.append(child)
    population = new_population
    scores = [0] * POPULATION_SIZE  # Reset scores for new generation

# Sensor data simulation
def get_sensor_data(car_x, car_y, car_angle):
    distances = []
    for angle_offset in [-45, 0, 45]:
        angle = math.radians(car_angle + angle_offset)
        for distance in range(1, 300):
            x = int(car_x + distance * math.cos(angle))
            y = int(car_y + distance * math.sin(angle))
            if 0 <= x < WIDTH and 0 <= y < HEIGHT and path_img.get_at((x, y)) != WHITE:
                distances.append(distance)
                break
        else:
            distances.append(300)
    return distances

# Check if the car is on the path
def is_car_on_path(car_rect):
    for point in car_rect:
        if 0 <= point[0] < WIDTH and 0 <= point[1] < HEIGHT:
            pixel_color = path_img.get_at((int(point[0]), int(point[1])))
            if pixel_color != WHITE:
                return False
    return True

# Reset AI car position
def reset_ai_car():
    global ai_car_x, ai_car_y, ai_car_speed, ai_car_angle, time_alive
    ai_car_x, ai_car_y = WIDTH // 2, HEIGHT - 400
    ai_car_speed = 0
    ai_car_angle = 0
    time_alive = 0

# Update AI car position
def update_ai_car():
    global ai_car_x, ai_car_y, ai_car_speed, ai_car_angle
    sensor_data = get_sensor_data(ai_car_x, ai_car_y, ai_car_angle)
    sensor_data = np.array(sensor_data + [ai_car_speed])
    outputs = population[current_ai].forward(sensor_data)
    turn, accelerate = outputs
    ai_car_angle += turn * 5
    ai_car_speed = min(max(ai_car_speed + accelerate * 0.2, -max_speed / 2), max_speed)
    ai_car_x -= ai_car_speed * math.sin(math.radians(ai_car_angle))
    ai_car_y -= ai_car_speed * math.cos(math.radians(ai_car_angle))
    rotated_car = pygame.transform.rotate(car_img, ai_car_angle)
    car_rect = rotated_car.get_rect(center=(ai_car_x, ai_car_y))
    screen.blit(rotated_car, car_rect.topleft)
    return car_rect

# Genetic Algorithm parameters
POPULATION_SIZE = 10
MUTATION_RATE = 0.1
population = [NeuralNetwork(input_size=4, hidden_size=6, output_size=2) for _ in range(POPULATION_SIZE)]
scores = [0] * POPULATION_SIZE
current_ai = 0

# Game variables
ai_car_x, ai_car_y = WIDTH // 2, HEIGHT - 400
ai_car_speed = 0
ai_car_angle = 0
time_alive = 0
max_speed = 5

# Main game loop
running = True
reset_ai_car()

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
        scores[current_ai] = time_alive
        current_ai += 1
        if current_ai >= POPULATION_SIZE:
            evolve_population()
            current_ai = 0
        reset_ai_car()

    # Update score for current AI
    time_alive += 1

    # Update display
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
