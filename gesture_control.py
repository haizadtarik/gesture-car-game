import pygame, sys
from pygame.locals import *
import random, time
import mediapipe as mp
import pygame.camera
import numpy as np
import cv2

# Initializing pygame and camera
pygame.init()
pygame.camera.init()

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
CAM_FEED_WIDTH = 200  # Width of the webcam feed area
CAM_FEED_HEIGHT = 150  # Height of the webcam feed area
TOTAL_WIDTH = SCREEN_WIDTH + CAM_FEED_WIDTH  # Add width for webcam feed

SPEED = 5
SCORE = 0

# Setting up Fonts
font = pygame.font.SysFont("Verdana", 60)
font_small = pygame.font.SysFont("Verdana", 30)
game_over = font.render("Game Over", True, BLACK)


# Update display to accommodate the webcam feed area
DISPLAYSURF = pygame.display.set_mode((TOTAL_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Game with Webcam Feed")

# MediaPipe Hand Detection setup
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils

# Initialize the camera and set up the feed size
cam = pygame.camera.Camera(pygame.camera.list_cameras()[0], (640, 480))
cam.start()

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
    # Get an image from the camera
    cam_frame = cam.get_image()

    # Flip the frame horizontally (mirror effect)
    frame = pygame.transform.flip(cam_frame, True, False)

    # Convert the frame to RGB array for MediaPipe processing
    frame_rgb = pygame.surfarray.array3d(frame)
    frame_rgb = frame_rgb.swapaxes(0, 1)  # Convert from pygame to MediaPipe format

    # Process the frame with MediaPipe
    result = hands.process(frame_rgb)
    

    hand_x = 0.5  # Default to center if no hand is detected
    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            # Get the x-coordinate of the index finger tip (landmark 8)
            index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            hand_x = index_finger_tip.x  # Normalized x-coordinate (0 to 1)

            frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_BGR2RGB)
            mp_drawing.draw_landmarks(frame_bgr, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_RGB2BGR)
            img_ccw = cv2.rotate(frame_rgb, cv2.ROTATE_90_COUNTERCLOCKWISE)
            frame = pygame.surfarray.make_surface(img_ccw)
            frame = pygame.transform.flip(frame, True, False)

    # Update game display and logic
    for event in pygame.event.get():
        if event.type == INC_SPEED:
            SPEED += 0.5     
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    # Fill the game display with white (playable area)
    DISPLAYSURF.fill(WHITE, pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))

    # Display the score
    scores = font.render('Score: ' + str(SCORE), True, BLACK)
    DISPLAYSURF.blit(scores, (10, 10))

    # Display the webcam feed in the non-playable area (right side of the screen)
    webcam_feed = pygame.transform.scale(frame, (CAM_FEED_WIDTH, CAM_FEED_HEIGHT))
    DISPLAYSURF.blit(webcam_feed, (SCREEN_WIDTH, SCREEN_HEIGHT - CAM_FEED_HEIGHT))

    # Moves and Re-draws all Sprites within the playable area
    DISPLAYSURF.blit(E1.image, E1.rect)
    E1.move()
    DISPLAYSURF.blit(P1.image, P1.rect)
    P1.move(hand_x)

    # To be run if collision occurs between Player and Enemy
    if pygame.sprite.spritecollideany(P1, enemies):
        time.sleep(0.5)

        DISPLAYSURF.fill(RED, pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))  # Fill only the playable area with red
        game_over_rect = game_over.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 10))
        DISPLAYSURF.blit(game_over, game_over_rect)
        final_scores = font_small.render('Final Score: ' + str(SCORE), True, BLACK)
        final_scores_rect = final_scores.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 40))
        DISPLAYSURF.blit(final_scores, final_scores_rect)
        
        # Draw restart button in the game area
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
