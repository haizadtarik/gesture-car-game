import pygame, sys
from pygame.locals import *
import random, time
 
#Initialzing 
pygame.init()
 
#Setting up FPS 
FPS = 60
FramePerSec = pygame.time.Clock()
 
#Creating colors
BLUE  = (0, 0, 255)
RED   = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
 
#Other Variables for use in the program
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
SPEED = 5
SCORE = 0
 
#Setting up Fonts
font = pygame.font.SysFont("Verdana", 60)
font_small = pygame.font.SysFont("Verdana", 20)
game_over = font.render("Game Over", True, BLACK)
 
# background = pygame.image.load("AnimatedStreet.png")
 
#Create a white screen 
DISPLAYSURF = pygame.display.set_mode((400,600))
DISPLAYSURF.fill(WHITE)
pygame.display.set_caption("Game")
 
class Enemy(pygame.sprite.Sprite):
      def __init__(self):
        super().__init__() 
        self.image = pygame.image.load("images/cone.png")
        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(40, SCREEN_WIDTH-40), 0)  
 
      def move(self):
        global SCORE
        self.rect.move_ip(0,SPEED)
        if (self.rect.top > 600):
            SCORE += 1
            self.rect.top = 0
            self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), 0)
 
 
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__() 
        self.image = pygame.image.load("images/car.png")
        self.rect = self.image.get_rect()
        self.rect.center = (160, 520)
        
    def move(self):
        pressed_keys = pygame.key.get_pressed()  
        if self.rect.left > 0:
              if pressed_keys[K_LEFT]:
                  self.rect.move_ip(-5, 0)
        if self.rect.right < SCREEN_WIDTH:        
              if pressed_keys[K_RIGHT]:
                  self.rect.move_ip(5, 0)

# Function to restart the game
def restart_game():
    global SPEED, SCORE, enemies, all_sprites, E1, P1
    SPEED = 5
    SCORE = 0
    E1 = Enemy()
    P1 = Player()
    enemies = pygame.sprite.Group()
    enemies.add(E1)
    all_sprites = pygame.sprite.Group()
    all_sprites.add(P1)
    all_sprites.add(E1)

# Function to create the restart button
def draw_restart_button():
    restart_text = font_small.render("Restart", True, BLACK)
    restart_text_rect = restart_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 100))
    padding = 10
    rect_width = restart_text_rect.width + padding * 2
    rect_height = restart_text_rect.height + padding * 2
    rect_x = restart_text_rect.x - padding
    rect_y = restart_text_rect.y - padding
    button_rect = pygame.Rect(rect_x, rect_y, rect_width, rect_height)
    pygame.draw.rect(DISPLAYSURF, GREEN, button_rect)
    DISPLAYSURF.blit(restart_text, restart_text_rect)
    return button_rect
                  
#Setting up Sprites        
P1 = Player()
E1 = Enemy()
 
#Creating Sprites Groups
enemies = pygame.sprite.Group()
enemies.add(E1)
all_sprites = pygame.sprite.Group()
all_sprites.add(P1)
all_sprites.add(E1)
 
#Adding a new User event 
INC_SPEED = pygame.USEREVENT + 1
pygame.time.set_timer(INC_SPEED, 1000)
 
#Game Loop
while True:
    #Cycles through all events occurring  
    for event in pygame.event.get():
        if event.type == INC_SPEED:
              SPEED += 0.5     
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
 
    # DISPLAYSURF.blit(background, (0,0))
    DISPLAYSURF.fill(WHITE)
    scores = font.render('Score: ' + str(SCORE), True, BLACK)
    DISPLAYSURF.blit(scores, (10,10))
 
    #Moves and Re-draws all Sprites
    for entity in all_sprites:
        DISPLAYSURF.blit(entity.image, entity.rect)
        entity.move()
 
    #To be run if collision occurs between Player and Enemy
    if pygame.sprite.spritecollideany(P1, enemies):
        time.sleep(0.5)
                    
        DISPLAYSURF.fill(RED)
        game_over_rect = game_over.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 10))
        DISPLAYSURF.blit(game_over, game_over_rect)
        final_scores = font_small.render('Final Score: ' + str(SCORE), True, BLACK)
        final_scores_rect = final_scores.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 40))
        DISPLAYSURF.blit(final_scores, final_scores_rect)
        

        # Draw restart button
        button_rect = draw_restart_button()
        pygame.display.update()

        # Wait for the player to click the restart button
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == MOUSEBUTTONDOWN:
                    if button_rect.collidepoint(event.pos):
                        restart_game()
                        waiting = False
                        break       
         
    pygame.display.update()
    FramePerSec.tick(FPS)