import pygame, sys
from pygame.locals import *
import random, time
import cv2
import mediapipe as mp

# Initializing pygame
pygame.init()

# Setting up FPS 
FPS = 60
FramePerSec = pygame.time.Clock()

# Creating colors
BLUE  = (0, 0, 255)
RED   = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Other Variables for use in the program
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
SPEED = 5
SCORE = 0

# Setting up Fonts
font = pygame.font.SysFont("Verdana", 60)
font_small = pygame.font.SysFont("Verdana", 30)
game_over = font.render("Game Over", True, BLACK)

# Create a white screen 
DISPLAYSURF = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
DISPLAYSURF.fill(WHITE)
pygame.display.set_caption("Game")

# MediaPipe Hand Detection setup
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils

# OpenCV video capture (for hand tracking)
cap = cv2.VideoCapture(0)

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__() 
        self.image = pygame.image.load("images/cone.png")
        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), 0)

    def move(self):
        global SCORE
        self.rect.move_ip(0, SPEED)
        if self.rect.top > SCREEN_HEIGHT:
            SCORE += 1
            self.rect.top = 0
            self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), 0)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__() 
        self.image = pygame.image.load("images/car.png")
        self.rect = self.image.get_rect()
        self.rect.center = (160, 520)

    def move(self, hand_x):
        # Map hand x-coordinate to the screen width
        self.rect.centerx = int(hand_x * SCREEN_WIDTH)

        # Keep the car within the screen boundaries
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH

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

# Setting up Sprites        
P1 = Player()
E1 = Enemy()

# Creating Sprites Groups
enemies = pygame.sprite.Group()
enemies.add(E1)
all_sprites = pygame.sprite.Group()
all_sprites.add(P1)
all_sprites.add(E1)

# Adding a new User event 
INC_SPEED = pygame.USEREVENT + 1
pygame.time.set_timer(INC_SPEED, 1000)

# Game Loop
while True:
    # OpenCV: Capture frame-by-frame
    ret, frame = cap.read()
    if not ret:
        break

    # Flip the frame horizontally (optional for a mirrored view)
    frame = cv2.flip(frame, 1)

    # Convert the BGR frame to RGB for MediaPipe processing
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_frame)

    hand_x = 0.5  # Default to center if no hand is detected
    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            # Get the x-coordinate of the index finger tip (landmark 8)
            index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            hand_x = index_finger_tip.x  # Normalized x-coordinate (0 to 1)

            # Optional: Draw hand landmarks on the frame
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    # Update game display and logic
    for event in pygame.event.get():
        if event.type == INC_SPEED:
            SPEED += 0.5     
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    DISPLAYSURF.fill(WHITE)
    scores = font.render('Score: ' + str(SCORE), True, BLACK)
    DISPLAYSURF.blit(scores, (10, 10))

    # Moves and Re-draws all Sprites
    DISPLAYSURF.blit(E1.image, E1.rect)
    E1.move()
    DISPLAYSURF.blit(P1.image, P1.rect)
    P1.move(hand_x)

    # To be run if collision occurs between Player and Enemy
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

    # Show OpenCV frame with hand tracking (for visualization)
    cv2.imshow('Hand Tracking', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release OpenCV resources
cap.release()
cv2.destroyAllWindows()
