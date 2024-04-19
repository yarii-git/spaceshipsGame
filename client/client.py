import pygame
import os
import socket
import pickle

# Initialize Pygame and its modules
pygame.font.init()
pygame.mixer.init()

# Set Dimensions
WIDTH, HEIGHT = 900, 500
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Client")

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

# Create a border rectangle
BORDER = pygame.Rect(WIDTH/2-5, 0, 10, HEIGHT)

# Set Bullet Sound Effects
BULLET_HIT_SOUND = pygame.mixer.Sound('Assets/GunHit.wav')
BULLET_FIRE_SOUND = pygame.mixer.Sound('Assets/GunFire.mp3')

# Initialize fonts
HEALTH_FONT = pygame.font.SysFont('comicsans', 40)
WINNER_FONT = pygame.font.SysFont('comicsans', 100)

# Set Frames Per Second
FPS = 60

# Set Velocity
VEL = 5
BULLET_VEL = 7

# Set Maximum Bullets
MAX_BULLETS = 3

# Set Spaceship dimensions
SPACESHIP_WIDTH, SPACESHIP_HEIGHT = 55, 40

YELLOW_HIT = pygame.USEREVENT + 1
RED_HIT = pygame.USEREVENT + 2


# Load and transform spaceship images
YELLOW_SPACESHIP_IMAGE = pygame.image.load(os.path.join("Assets", "spaceship_yellow.png"))
YELLOW_SPACESHIP = pygame.transform.rotate(pygame.transform.scale( YELLOW_SPACESHIP_IMAGE, (SPACESHIP_WIDTH, SPACESHIP_HEIGHT)), 90)
RED_SPACESHIP_IMAGE = pygame.image.load(os.path.join("Assets", "spaceship_red.png"))
RED_SPACESHIP = pygame.transform.rotate(pygame.transform.scale(RED_SPACESHIP_IMAGE, (SPACESHIP_WIDTH, SPACESHIP_HEIGHT)), 270)
SPACE = pygame.transform.scale(pygame.image.load(os.path.join('Assets', 'space.png')), (WIDTH, HEIGHT))

# Define Ship class
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
        if keys_pressed[pygame.K_LEFT] and self.x - VEL > BORDER.x + BORDER.width:
            self.x -= VEL
        if keys_pressed[pygame.K_RIGHT] and self.x + VEL + self.width < WIDTH:
            self.x += VEL
        if keys_pressed[pygame.K_UP] and self.y - VEL > 0:
            self.y -= VEL
        if keys_pressed[pygame.K_DOWN] and self.y + VEL + self.height < HEIGHT - 15:
            self.y += VEL


# Define draw_window function
def draw_window(red, yellow):
    WIN.blit(SPACE, (0, 0))
    pygame.draw.rect(WIN, BLACK, BORDER)

    # Draw Red Spaceship information
    red_health_text = HEALTH_FONT.render("Health: " + str(red.health), 1, WHITE)
    WIN.blit(red_health_text, (WIDTH - red_health_text.get_width() - 10, 10))
    WIN.blit(RED_SPACESHIP, (red.x, red.y))
    for bullet in red.bullets:
        pygame.draw.rect(WIN, RED, bullet)
   
    # Draw Yellow Spaceship information
    yellow_health_text = HEALTH_FONT.render("Health: " + str(yellow.health), 1, WHITE)
    WIN.blit(yellow_health_text, (10, 10))
    WIN.blit(YELLOW_SPACESHIP, (yellow.x, yellow.y))
    for bullet in yellow.bullets:
        pygame.draw.rect(WIN, YELLOW, bullet)
   
    pygame.display.update()


# Define handle_bullets function
def handle_bullets(playerRed, playerYellow):
    remove_bullets = []

    for bullet in playerRed.bullets:
        bullet.x -= BULLET_VEL
        # Check if the bullet hits the Yellow Spaceship
        if playerYellow.x < bullet.x < playerYellow.x + playerYellow.width and playerYellow.y < bullet.y < playerYellow.y + playerYellow.height:
            # Decrease Yellow Spaceship health
            playerYellow.health -= 1
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
    winner_text = ""
    clock = pygame.time.Clock()
    yellow = Ship(100, 300)
    red = Ship(700, 300)
    pressed_keys = {}
    

    # Set up client
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.connect(("127.0.0.1", 5555))
    
    while run:
        
        clock.tick(FPS)

        # Handle bullets
        remove_bullets = handle_bullets(red, yellow)

        #Chech for winner
        if red.health <= 0:
            winner_text = "Yellow player wins!"

        # Remove bullets
        for bullet in remove_bullets:
            red.bullets.remove(bullet)
        
        # Get server data
        data = server_socket.recv(4096)

        # Chech for winner
        if data == b'WIN': 
            draw_winner("Red player wins!")  
            break

        #Update yellow data and red health
        red_data, yellow_data = pickle.loads(data)
        yellow.x = yellow_data.x
        yellow.y = yellow_data.y
        red.health = red_data.health
        yellow.bullets = yellow_data.bullets

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RCTRL and len(yellow.bullets) < MAX_BULLETS:
                    
                    bullet = pygame.Rect(
                        red.x - red.width, red.y + red.height // 2 - 2, 10, 5)
                    red.bullets.append(bullet)
                    BULLET_FIRE_SOUND.play()

                
            # Update keys
            if event.type == pygame.KEYDOWN:
                pressed_keys[event.key] = True
            elif event.type == pygame.KEYUP:
                pressed_keys[event.key] = False
            
        # Update the pressed keys dictionary
        keys_pressed = pygame.key.get_pressed()
        red.move(keys_pressed)


        # Send updated data to the server
        dataClient = pickle.dumps((red, yellow))
        server_socket.send(dataClient)

        # Draw the game window
        draw_window(red, yellow)

        # Send winner to the server
        if winner_text:
            server_socket.send("WIN".encode())  
            draw_winner(winner_text)
            break

    # Clean up and quit Pygame
    pygame.quit()

# Call the main function
if __name__ == "__main__":
    main()
