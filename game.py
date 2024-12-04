import pygame
import sys
import math

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 1920, 1080
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Top-View Race Game")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Clock and FPS
clock = pygame.time.Clock()
FPS = 60

# Load assets
car_img = pygame.image.load("car.png")  # Replace with your car image
car_img = pygame.transform.scale(car_img, (30, 30))  # Resize car
path_img = pygame.image.load("track.png")  # Replace with your path image
path_img = pygame.transform.scale(path_img, (WIDTH, HEIGHT))  # Scale to fit screen

# Font for messages
font = pygame.font.SysFont(None, 74)
small_font = pygame.font.SysFont(None, 36)
game_over_text = font.render("Game Over", True, RED)
replay_text = small_font.render("Replay", True, WHITE)

# Replay button dimensions
button_width, button_height = 200, 50
button_x, button_y = WIDTH // 2 - button_width // 2, HEIGHT // 2 + 50

# Reset game variables
def reset_game():
    global car_x, car_y, car_speed, car_angle, game_over
    car_x, car_y = WIDTH // 2, HEIGHT - 400
    car_speed = 0
    car_angle = 0
    game_over = False

# Initial car properties
car_x, car_y = WIDTH // 2, HEIGHT - 400
car_speed = 0
car_angle = 0
rotation_speed = 5
max_speed = 5
acceleration = 0.2
deceleration = 0.1
game_over = False

# Function to check if the car is on the path
def is_car_on_path(car_rect):
    for point in car_rect:
        if 0 <= point[0] < WIDTH and 0 <= point[1] < HEIGHT:
            pixel_color = path_img.get_at((int(point[0]), int(point[1])))
            if pixel_color != WHITE:
                return False  # Car is off the path
    return True

# Game loop
running = True
while running:
    screen.fill(BLACK)
    screen.blit(path_img, (0, 0))

    if game_over:
        # Display Game Over message and replay button
        screen.fill(BLACK)
        screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 100))
        pygame.draw.rect(screen, BLUE, (button_x, button_y, button_width, button_height))
        screen.blit(replay_text, (button_x + button_width // 2 - replay_text.get_width() // 2, button_y + button_height // 2 - replay_text.get_height() // 2))

        # Check for button click
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                print("clicked")
                mouse_x, mouse_y = event.pos
                if button_x <= mouse_x <= button_x + button_width and button_y <= mouse_y <= button_y + button_height:
                    reset_game()  # Restart the game
        pygame.display.flip()
        continue

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Key handling
    keys = pygame.key.get_pressed()
    if keys[pygame.K_a]:
        car_angle += rotation_speed
    if keys[pygame.K_d]:
        car_angle -= rotation_speed
    if keys[pygame.K_w]:
        car_speed = min(car_speed + acceleration, max_speed)
    elif keys[pygame.K_s]:
        car_speed = max(car_speed - deceleration, -max_speed / 2)
    else:
        car_speed *= 0.95  # Gradual slowdown

    # Calculate new position
    car_x -= car_speed * math.sin(math.radians(car_angle))
    car_y -= car_speed * math.cos(math.radians(car_angle))  # Negative because y-axis is inverted in Pygame

    # Rotate and draw car
    rotated_car = pygame.transform.rotate(car_img, car_angle)
    car_rect = rotated_car.get_rect(center=(car_x, car_y))
    screen.blit(rotated_car, car_rect.topleft)

    # Visualize the hitbox (using car_rect)
    pygame.draw.rect(screen, RED, car_rect, 2)  # Draw the car's hitbox in red

    # Create and visualize a custom hitbox
    hitbox_width, hitbox_height = 25, 20
    custom_hitbox = pygame.Rect(0, 0, hitbox_width, hitbox_height)
    custom_hitbox.center = car_rect.center  # Align custom hitbox with car center
    pygame.draw.rect(screen, BLUE, custom_hitbox, 2)  # Draw custom hitbox in blue

    # Check if car is on the path using the custom hitbox
    points_to_check = [
        custom_hitbox.topleft,
        custom_hitbox.topright,
        custom_hitbox.bottomleft,
        custom_hitbox.bottomright,
    ]
    if not is_car_on_path(points_to_check):
        game_over = True  # Trigger game over state

    # Update display
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
