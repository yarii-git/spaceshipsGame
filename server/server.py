import pygame
import os
import socket
import pickle

# Initialize Pygame
pygame.font.init()
pygame.mixer.init()

# Set Dimensions
WIDTH, HEIGHT = 900, 500
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Server")

# Set Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

# Set Border
BORDER = pygame.Rect(WIDTH/2-5, 0, 10, HEIGHT)

# Set Sound Effects
BULLET_HIT_SOUND = pygame.mixer.Sound('Assets/GunHit.wav')
BULLET_FIRE_SOUND = pygame.mixer.Sound('Assets/GunFire.mp3')

# Set Fonts
HEALTH_FONT = pygame.font.SysFont('comicsans', 40)
WINNER_FONT = pygame.font.SysFont('comicsans', 100)

# Set Game Variables
FPS = 60
VEL = 5
BULLET_VEL = 7
MAX_BULLETS = 3
SPACESHIP_WIDTH, SPACESHIP_HEIGHT = 55, 40

# Set Custom Events
YELLOW_HIT = pygame.USEREVENT + 1
RED_HIT = pygame.USEREVENT + 2

# Load Images
YELLOW_SPACESHIP_IMAGE = pygame.image.load(os.path.join("Assets", "spaceship_yellow.png"))
YELLOW_SPACESHIP = pygame.transform.rotate(pygame.transform.scale(YELLOW_SPACESHIP_IMAGE, (SPACESHIP_WIDTH, SPACESHIP_HEIGHT)), 90)
RED_SPACESHIP_IMAGE = pygame.image.load(os.path.join("Assets", "spaceship_red.png"))
RED_SPACESHIP = pygame.transform.rotate(pygame.transform.scale(RED_SPACESHIP_IMAGE, (SPACESHIP_WIDTH, SPACESHIP_HEIGHT)), 270)

SPACE = pygame.transform.scale(pygame.image.load(os.path.join('Assets', 'space.png')), (WIDTH, HEIGHT))

#Ship class
class Ship:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = SPACESHIP_WIDTH
        self.height = SPACESHIP_HEIGHT
        self.bullets = []
        self.health = 10

    # Define move method for the Ship class
    def move(self, keys_pressed):
        if keys_pressed[pygame.K_a] and self.x - VEL > 0: 
            self.x -= VEL
        if keys_pressed[pygame.K_d] and self.x + VEL + self.width < BORDER.x:
            self.x += VEL
        if keys_pressed[pygame.K_w] and self.y - VEL > 0:
            self.y -= VEL
        if keys_pressed[pygame.K_s] and self.y + VEL + self.height < HEIGHT - 15:
            self.y += VEL

def draw_window(red, yellow):
    WIN.blit(SPACE, (0, 0))
    pygame.draw.rect(WIN, BLACK, BORDER)

    # Dibuixa la informació de la nau vermella
    red_health_text = HEALTH_FONT.render("Health: " + str(red.health), 1, WHITE)
    WIN.blit(red_health_text, (WIDTH - red_health_text.get_width() - 10, 10))
    WIN.blit(RED_SPACESHIP, (red.x, red.y))
    for bullet in red.bullets:
        pygame.draw.rect(WIN, RED, bullet)
   
    # Dibuixa la informació de la nau groga
    yellow_health_text = HEALTH_FONT.render("Health: " + str(yellow.health), 1, WHITE)
    WIN.blit(yellow_health_text, (10, 10))
    WIN.blit(YELLOW_SPACESHIP, (yellow.x, yellow.y))
    for bullet in yellow.bullets:
        pygame.draw.rect(WIN, YELLOW, bullet)
   
    pygame.display.update()

# Define handle_bullets function
def handle_bullets(playerRed, playerYellow):
    remove_bullets = []

    # Check if the bullet hits the Red Spaceship
    for bullet in playerYellow.bullets:
        bullet.x += BULLET_VEL
        # Si la bala passa per la posició en la que es troba la nau groga...
        if playerRed.x < bullet.x < playerRed.x + playerRed.width and playerRed.y < bullet.y < playerRed.y + playerRed.height:
            # Decrease Red Spaceship health
            playerRed.health -= 1
            # Play bullet hit sound
            BULLET_HIT_SOUND.play()
            # Add bullet to remove_bullets list
            remove_bullets.append(bullet)
        # Remove bullet if it goes off-screen
        if bullet.x < 0:
            remove_bullets.append(bullet)
    
    return remove_bullets


# Define draw_winner function
def draw_winner(text):
    draw_text = WINNER_FONT.render(text, 1, WHITE)
    WIN.blit(draw_text, (WIDTH/2 - draw_text.get_width() / 2, HEIGHT/2 - draw_text.get_height()/2))
    pygame.display.update()
    pygame.time.delay(5000)

# Define main function
def main():
    run = True
    red = Ship(700,300)
    yellow = Ship(100,300)
    winner_text = ""
    pressed_keys = {}

    clock = pygame.time.Clock()

    # Set up server
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("127.0.0.1", 5555))
    server_socket.listen()

    client_socket, address = server_socket.accept()
    print(f"Connection from {address} has been established.")

    
    while run:
        clock.tick(FPS)

        # Handle bullets
        remove_bullets = handle_bullets(red, yellow)

        #Chech for winner
        if yellow.health <= 0:
            winner_text = "Red player wins!"
        
        # Remove bullets
        for bullet in remove_bullets:
            yellow.bullets.remove(bullet)
        

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()

            # Handle events
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LCTRL and len(yellow.bullets) < MAX_BULLETS:
                    bullet = pygame.Rect(
                        yellow.x + yellow.width, yellow.y + yellow.height//2 - 2, 10, 5)
                    yellow.bullets.append(bullet)
                    BULLET_FIRE_SOUND.play()
            
            # Update keys
            if event.type == pygame.KEYDOWN:
                pressed_keys[event.key] = True
            elif event.type == pygame.KEYUP:
                pressed_keys[event.key] = False

        # Update the pressed keys dictionary
        keys_pressed = pygame.key.get_pressed()
        yellow.move(keys_pressed)

        # Send updated data to the client
        data = pickle.dumps((red, yellow))
        client_socket.send(data)

        # Get client data
        clientData = client_socket.recv(4096)

        # Chech for winner
        if clientData == b'WIN': 
            draw_winner("Yellow player wins!")  
            break

        #Update red data and yellow health
        red_data, yellow_data = pickle.loads(clientData)
        red.x = red_data.x
        red.y = red_data.y
        yellow.health = yellow_data.health
        red.bullets = red_data.bullets

        # Draw the game window
        draw_window(red, yellow)

        # Send winner to the client
        if winner_text:
            client_socket.send("WIN".encode()) 
            draw_winner(winner_text)
            break
    
    # Clean up and quit Pygame
    pygame.quit()

# Call the main function
if __name__ == "__main__":
    main()
