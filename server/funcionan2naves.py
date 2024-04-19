import pygame
import os
import socket
import json

pygame.font.init()
pygame.mixer.init()

# Set Dimensions
WIDTH, HEIGHT = 900, 500
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Server")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

BORDER = pygame.Rect(WIDTH/2-5, 0, 10, HEIGHT)

# Set Bullet Sound Effects
BULLET_HIT_SOUND = pygame.mixer.Sound('Assets/GunHit.wav')
BULLET_FIRE_SOUND = pygame.mixer.Sound('Assets/GunFire.mp3')

HEALTH_FONT = pygame.font.SysFont('comicsans', 40)
WINNER_FONT = pygame.font.SysFont('comicsans', 100)

FPS = 60
VEL = 5
BULLET_VEL = 7
MAX_BULLETS = 3
SPACESHIP_WIDTH, SPACESHIP_HEIGHT = 55, 40

YELLOW_HIT = pygame.USEREVENT + 1
RED_HIT = pygame.USEREVENT + 2

YELLOW_SPACESHIP_IMAGE = pygame.image.load(
    os.path.join("Assets", "spaceship_yellow.png"))
YELLOW_SPACESHIP = pygame.transform.rotate(pygame.transform.scale(
    YELLOW_SPACESHIP_IMAGE, (SPACESHIP_WIDTH, SPACESHIP_HEIGHT)), 90)
RED_SPACESHIP_IMAGE = pygame.image.load(
    os.path.join("Assets", "spaceship_red.png"))
RED_SPACESHIP = pygame.transform.rotate(pygame.transform.scale(
    RED_SPACESHIP_IMAGE, (SPACESHIP_WIDTH, SPACESHIP_HEIGHT)), 270)

SPACE = pygame.transform.scale(pygame.image.load(
    os.path.join('Assets', 'space.png')), (WIDTH, HEIGHT))


def draw_window(red, yellow, red_bullets, yellow_bullets, red_health, yellow_health):
    WIN.blit(SPACE, (0, 0))
    pygame.draw.rect(WIN, BLACK, BORDER)

    red_health_text = HEALTH_FONT.render(
        "Health: " + str(red_health), 1, WHITE)
    yellow_health_text = HEALTH_FONT.render(
        "Health: " + str(yellow_health), 1, WHITE)
    WIN.blit(red_health_text, (WIDTH - red_health_text.get_width() - 10, 10))
    WIN.blit(yellow_health_text, (10, 10))

    if yellow:
        WIN.blit(YELLOW_SPACESHIP, (yellow["x"], yellow["y"]))
    if red:
        WIN.blit(RED_SPACESHIP, (red["x"], red["y"]))

    for bullet in red_bullets:
        pygame.draw.rect(WIN, RED, bullet)
    for bullet in yellow_bullets:
        pygame.draw.rect(WIN, YELLOW, bullet)

    pygame.display.update()


def red_handle_movement(keys_pressed, red):
    if keys_pressed[pygame.K_LEFT] and red["x"] - VEL > BORDER.x + BORDER.width:  # LEFT
        red["x"] -= VEL
    if keys_pressed[pygame.K_RIGHT] and red["x"] + VEL + SPACESHIP_WIDTH < WIDTH:  # RIGHT
        red["x"] += VEL
    if keys_pressed[pygame.K_UP] and red["y"] - VEL > 0:  # UP
        red["y"] -= VEL
    if keys_pressed[pygame.K_DOWN] and red["y"] + VEL + SPACESHIP_HEIGHT < HEIGHT - 15:  # DOWN
        red["y"] += VEL

# def yellow_handle_movement(keys_pressed, yellow):
#     if keys_pressed:
#         if keys_pressed[pygame.K_a] and yellow["x"] - VEL > 0:  # LEFT
#             yellow["x"] -= VEL
#         if keys_pressed[pygame.K_d] and yellow["x"] + VEL + SPACESHIP_WIDTH < BORDER.x:  # RIGHT
#             yellow["x"] += VEL
#         if keys_pressed[pygame.K_w] and yellow["y"] - VEL > 0:  # UP
#             yellow["y"] -= VEL
#         if keys_pressed[pygame.K_s] and yellow["y"] + VEL + SPACESHIP_HEIGHT < HEIGHT - 15:  # DOWN
#             yellow["y"] += VEL

def main():
    red = {"x": 700, "y": 300}
    yellow = {"x": 100, "y": 300}

    red_bullets = []
    yellow_bullets = []

    red_health = 10
    yellow_health = 10

    clock = pygame.time.Clock()

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("127.0.0.1", 5555))
    server_socket.listen()

    client_socket, address = server_socket.accept()
    print(f"Connection from {address} has been established.")

    run = True
    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()

        # Controlar al jugador rojo (servidor)
        keys_pressed = pygame.key.get_pressed()
        red_handle_movement(keys_pressed, red)

        # Esperar a recibir teclas presionadas del cliente
        # message = client_socket.recv(1024).decode()
        # client_keys_pressed = json.loads(message)
        # Enviar posiciones de los jugadores al cliente
        positions_data = {
            "red_x": red["x"],
            "red_y": red["y"],
            # "yellow_x": yellow["x"],
            # "yellow_y": yellow["y"]
        }
        message = json.dumps(positions_data)
        client_socket.send(message.encode())
        
        positions_data_json = client_socket.recv(1024).decode()
        client_positions_data = json.loads(positions_data_json)

        # yellow_handle_movement(client_keys_pressed, yellow)

        yellow["x"] = client_positions_data["yellow_x"]
        yellow["y"] = client_positions_data["yellow_y"]

        # Pintar el tablero después de procesar las acciones
        draw_window(red, yellow, red_bullets, yellow_bullets, red_health, yellow_health)

    pygame.quit()


if __name__ == "__main__":
    main()
