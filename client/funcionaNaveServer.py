import pygame 
import os
import socket
import json

pygame.font.init()
pygame.mixer.init()

# Set Dimensions
WIDTH, HEIGHT = 900, 500
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("First Game!")

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
        WIN.blit(YELLOW_SPACESHIP, (yellow.x, yellow.y))
    if red:
        WIN.blit(RED_SPACESHIP, (red.x, red.y))

    if red_bullets is not None:
        for bullet in red_bullets:
            pygame.draw.rect(WIN, RED, bullet)
    if yellow_bullets is not None:
        for bullet in yellow_bullets:
            pygame.draw.rect(WIN, YELLOW, bullet)

    pygame.display.update()



def yellow_handle_movement(keys_pressed, yellow):
    if keys_pressed:
        if keys_pressed[pygame.K_a] and yellow.x - VEL > 0:  # LEFT
            yellow.x -= VEL
        if keys_pressed[pygame.K_d] and yellow.x + VEL + yellow.width < BORDER.x:  # RIGHT
            yellow.x += VEL
        if keys_pressed[pygame.K_w] and yellow.y - VEL > 0:  # UP
            yellow.y -= VEL
        if keys_pressed[pygame.K_s] and yellow.y + VEL + yellow.height < HEIGHT - 15:  # DOWN
            yellow.y += VEL


def main():
    yellow = pygame.Rect(100, 300, SPACESHIP_WIDTH, SPACESHIP_HEIGHT)

    yellow_bullets = []

    yellow_health = 10

    clock = pygame.time.Clock()

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.connect(("127.0.0.1", 5555))

    run = True
    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()

        # Enviar teclas presionadas al servidor
        keys_pressed = pygame.key.get_pressed()
        message = ','.join(str(int(key)) for key in keys_pressed)
        server_socket.send(message.encode())

        # Recibir posiciones de los jugadores del servidor
        positions_data_json = server_socket.recv(1024).decode()
        positions_data = json.loads(positions_data_json)

        # Actualizar la posición del jugador amarillo
        yellow.x = positions_data["yellow_x"]
        yellow.y = positions_data["yellow_y"]

        # Pintar el tablero después de procesar las acciones
        draw_window(None, yellow, None, yellow_bullets, None, yellow_health)

    pygame.quit()


if __name__ == "__main__":
    main()
