from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import time
import random

# Camera-related variables
camera_pos = (0, 500, 500)
camera_angle = 0
camera_height = 1000
camera_mode = "tpp"  # "tpp" (third-person) or "fpp" (first-person)

# Player stats
player_health = 100
player_lives = 5
displayed_health = float(player_health)

# FPP offsets and arrow firing offset
EYE_OFFSET_X = 0.0
EYE_OFFSET_Y = 0.0
EYE_OFFSET_Z = 0.95
ARROW_FIRING_OFFSET = 5.0

MAX_LIVES = 7

# Platform dimensions (using scaling where needed)
PLATFORM_WIDTH = 900 * 1.5
PLATFORM_LENGTH = 1800 * 1.5
PLATFORM_THICKNESS = 20
GAP_WIDTH = 30 * 1.5
PLATFORM_HEIGHT = 0

# Lists for obstacles and clouds
obstacles = []
clouds = []

# Obstacles settings – trees and bushes
TREE_OBSTACLE_COUNT = 4
BUSH_OBSTACLE_COUNT = 4
TREE_RADIUS = 30
BUSH_RADIUS = 25
TREE_HEIGHT = 200       
BUSH_HEIGHT = 50
TREE_COLOR = (0.0, 0.3, 0.0)
BUSH_COLOR = (0.0, 0.3, 0.0)

# Cloud settings
NUM_CLOUDS = 20
CLOUD_MARGIN = 300
CLOUD_MIN_Z = 600
CLOUD_MAX_Z = 800

# Collision and archer settings
PLAYER_COLLISION_RADIUS = 10
ARCHER_HEIGHT = 100
archer_pos = [0, 0, PLATFORM_HEIGHT + PLATFORM_THICKNESS/2]
archer_rotation = 0
archer_velocity = [0, 0, 0]
archer_jumping = False
archer_jump_start_time = 0
JUMP_HEIGHT = ARCHER_HEIGHT
JUMP_DURATION = 1.0
GRAVITY = -6.8

# Walking animation
walking = False
leg_angle = 0
leg_direction = 1
walk_speed = 5

# Player position for camera tracking
player_pos = [0, 0, PLATFORM_HEIGHT + PLATFORM_THICKNESS/2]

# Aiming and shooting parameters
aiming = False
aim_z_offset = 0
crosshair_size = 10
arrows = []
ARROW_SPEED = 10
ARROW_LIFETIME = 3.0

fovY = 60

# Balloon-related variables
balloons = []
MAX_BALLOONS = 40  # Game over triggered 
BALLOON_SPAWN_INTERVAL = 3.0
last_balloon_spawn_time = time.time()
game_over = False
player_score = 0

normal_balloons_popped_count = 0
power_up_active = None
power_up_end_time = 0
POWERUP_LIFETIME = 20.0

balloons_popped_total = 0
golden_balloon_notification = ""
GOLDEN_THRESHOLD = 20
GOLDEN_LIFETIME = 20.0

BALLOON_COLORS = {
    "grey": {"color": (0.7, 0.7, 0.7), "points": 5, "probability": 0.5},
    "black": {"color": (0.3, 0.3, 0.3), "points": 10, "probability": 0.28},
    "blue": {"color": (0.2, 0.2, 0.9), "points": 20, "probability": 0.1},
    "light_green": {"color": (0.5, 0.9, 0.5), "points": 0, "probability": 0.05, "effect": "health"},
    "red": {"color": (0.9, 0.2, 0.2), "points": 0, "probability": 0.03, "effect": "life"},
    "lava": {"color": (0.9, 0.4, 0.1), "points": 0, "probability": 0.02, "effect": "lava"},
    "purple": {"color": (0.7, 0.3, 0.9), "points": 0, "probability": 0.02, "effect": "purple"}
}

# Platform effect variables
left_platform_effect = None
right_platform_effect = None
left_platform_effect_start_time = 0
right_platform_effect_start_time = 0
platform_effect_duration = 30.0
effect_damage_interval = 3.0
last_effect_damage_time = 0
hazardous_balloons = {}

BALLOON_SPEED = 0.3

# Pause/Quit UI globals
game_paused = False
PAUSE_BUTTON_CENTER = (920, 780)
PAUSE_BUTTON_RADIUS = 20
QUIT_BUTTON_CENTER = (860, 780)
QUIT_BUTTON_SIZE = 30


def draw_humanoid():
    """Draw a humanoid figure with a bow at archer_pos"""
    glPushMatrix()
   
    # Apply position and rotation
    glTranslatef(archer_pos[0], archer_pos[1], archer_pos[2])
    glRotatef(archer_rotation, 0, 0, 1)  # Rotate around z-axis
   
    # Define body parts proportions relative to ARCHER_HEIGHT
    head_radius = ARCHER_HEIGHT * 0.15
    torso_height = ARCHER_HEIGHT * 0.4
    arm_length = ARCHER_HEIGHT * 0.35
    leg_length = ARCHER_HEIGHT * 0.4
   
    # Draw head (sphere)
    glColor3f(0.8, 0.6, 0.5)  # Skin color
    glPushMatrix()
    glTranslatef(0, 0, ARCHER_HEIGHT - head_radius)
    glutSolidSphere(head_radius, 10, 10)
    glPopMatrix()
   
    # Draw torso (cuboid)
    glPushMatrix()
    glTranslatef(0, 0, ARCHER_HEIGHT - head_radius*2 - torso_height/2)
    glColor3f(0.3, 0.3, 0.3)  # Dark ash color for clothing
    glScalef(head_radius*1.5, head_radius, torso_height)
    glutSolidCube(1.0)
    glPopMatrix()
   
    # Draw arms
    # Right arm (holding bow) - pointing forward horizontally
    glPushMatrix()
    glTranslatef(head_radius*1.5, head_radius*2, ARCHER_HEIGHT - head_radius*2 - torso_height/4)
    glColor3f(0.8, 0.6, 0.5)  # Skin color
    glRotatef(0, 0, 1, 0)  # Point forward (along y-axis)
    glScalef(head_radius/2, arm_length, head_radius/2)
    glutSolidCube(1.0)
    glPopMatrix()
   
    # Left arm (draw bow) - pointing forward
    glPushMatrix()
    glTranslatef(-head_radius*1.5, head_radius*2, ARCHER_HEIGHT - head_radius*2 - torso_height/4)
    glColor3f(0.8, 0.6, 0.5)  # Skin color
    glRotatef(0, 0, 1, 0)  # Point forward (along y-axis)
    glScalef(head_radius/2, arm_length, head_radius/2)
    glutSolidCube(1.0)
    glPopMatrix()
   
    # Draw legs with animation
    # Left leg
    glPushMatrix()
    glTranslatef(-head_radius*0.75, 0, ARCHER_HEIGHT - head_radius*2 - torso_height)
    if walking:
        glRotatef(leg_angle, 1, 0, 0)  # Rotate around x-axis for walking
    glColor3f(0.6, 0.6, 0.6)  # Light ash color for pants
    glScalef(head_radius/2, head_radius/2, leg_length)
    glutSolidCube(1.0)
    glPopMatrix()
   
    # Right leg
    glPushMatrix()
    glTranslatef(head_radius*0.75, 0, ARCHER_HEIGHT - head_radius*2 - torso_height)
    if walking:
        glRotatef(-leg_angle, 1, 0, 0)  # Opposite rotation for alternate leg
    glColor3f(0.6, 0.6, 0.6)  # Light ash color for pants
    glScalef(head_radius/2, head_radius/2, leg_length)
    glutSolidCube(1.0)
    glPopMatrix()
   
    # Draw bow
    draw_bow()
   
    glPopMatrix()



def draw_bow():
    """Draw a simple bow in the archer's hand (without the string)"""
    # Draw the bow as a curved line
    glColor3f(0.6, 0.3, 0.1)  # Brown color for bow
   
    # Draw bow positioned horizontally in front of the figure
    glLineWidth(3.0)
    glBegin(GL_LINE_STRIP)
    for i in range(11):
        angle = math.radians(i * 18 - 90)  # Create a 180-degree curved line
        y = 50 * math.cos(angle)  # Positioned forward (y-axis)
        z = 30 * math.sin(angle)  # Up/down (z-axis)
        glVertex3f(30, y, z + ARCHER_HEIGHT*0.6)  # Positioned to the right side of the body, forward facing
    glEnd()
    glLineWidth(1.0)
    # Note: Bow string removed as requested



def update_archer_physics():
    """Update archer position based on physics"""
    global archer_pos, archer_velocity, archer_jumping, archer_jump_start_time
   
    current_time = time.time()
   
    if archer_jumping:
        elapsed = current_time - archer_jump_start_time
        if elapsed >= JUMP_DURATION:
            archer_jumping = False
            archer_pos[2] = PLATFORM_HEIGHT + PLATFORM_THICKNESS/2
        else:
            progress = elapsed / JUMP_DURATION
            height_factor = math.sin(progress * math.pi)
            archer_pos[2] = PLATFORM_HEIGHT + PLATFORM_THICKNESS/2 + height_factor * JUMP_HEIGHT
   
    left_platform_right = -GAP_WIDTH/2
    left_platform_left = left_platform_right - PLATFORM_WIDTH
    right_platform_left = GAP_WIDTH/2
    right_platform_right = right_platform_left + PLATFORM_WIDTH
   
    platform_front = PLATFORM_LENGTH/2
    platform_back = -PLATFORM_LENGTH/2
   
    if (archer_pos[0] < left_platform_left or archer_pos[0] > right_platform_right or
        archer_pos[1] < platform_back or archer_pos[1] > platform_front):
        archer_pos = [0, 0, PLATFORM_HEIGHT + PLATFORM_THICKNESS/2]
        archer_rotation = 0
        archer_velocity = [0, 0, 0]


def update_leg_animation():
    """Update leg animation for walking"""
    global leg_angle, leg_direction, walking
   
    if walking:
        leg_angle += leg_direction * walk_speed
        if leg_angle > 30:
            leg_direction = -1
        elif leg_angle < -30:
            leg_direction = 1
    else:
        if abs(leg_angle) < walk_speed:
            leg_angle = 0
        elif leg_angle > 0:
            leg_angle = max(0, leg_angle - walk_speed*2)
        elif leg_angle < 0:
            leg_angle = min(0, leg_angle + walk_speed*2)


def constrain_archer_position():
    """
    Ensures the archer stays within platform boundaries and does not pass through obstacles.
    If a collision with an obstacle is detected, reverts to the previous valid position.
    """
    global archer_pos, prev_archer_pos

    left_platform_right = -GAP_WIDTH / 2
    left_platform_left = left_platform_right - PLATFORM_WIDTH
    right_platform_left = GAP_WIDTH / 2
    right_platform_right = right_platform_left + PLATFORM_WIDTH
    platform_front = PLATFORM_LENGTH / 2
    platform_back = -PLATFORM_LENGTH / 2

    if archer_pos[0] < left_platform_left:
        archer_pos[0] = left_platform_left
    elif archer_pos[0] > right_platform_right:
        archer_pos[0] = right_platform_right

    if archer_pos[1] < platform_back:
        archer_pos[1] = platform_back
    elif archer_pos[1] > platform_front:
        archer_pos[1] = platform_front

    # Check and undo any move that causes a collision with obstacles (e.g., trees)
    if is_colliding_with_obstacle(archer_pos, PLAYER_COLLISION_RADIUS):
        archer_pos[0], archer_pos[1] = prev_archer_pos[0], prev_archer_pos[1]


def reset_game():
    """Reset the game state"""
    global archer_pos, archer_rotation, archer_velocity, archer_jumping
    global balloons, player_score, game_over, last_balloon_spawn_time
    global player_health, player_lives, hazardous_balloons
    global left_platform_effect, right_platform_effect
    global displayed_health

    archer_pos = [0, 0, PLATFORM_HEIGHT + PLATFORM_THICKNESS/2]
    archer_rotation = 0
    archer_velocity = [0, 0, 0]
    archer_jumping = False

    balloons = []
    arrows = []
    hazardous_balloons = {}

    player_score = 0
    game_over = False
    last_balloon_spawn_time = time.time()

    player_health = 100
    player_lives = 5
    displayed_health = player_health

    left_platform_effect = None
    right_platform_effect = None
    spawn_obstacles()
    spawn_clouds()



def keyboardListener(key, x, y):
    """
    Handles keyboard inputs for player movement and archer interaction.
    Now computes a tentative new position and only updates it if no obstacle collision is detected.
    """
    global archer_rotation, archer_velocity, archer_jumping, archer_jump_start_time, walking
    global camera_mode, archer_pos, aim_z_offset, aiming, game_over, prev_archer_pos, game_paused
    global player_pos

    # Ignore inputs if game over or paused (except for reset)
    if game_over and key != b'r':
        return
    if game_paused and key != b'r':
        return

    movement_speed = 10
    rotation_speed = 5
    aim_speed = 0.05

    # Store the previous valid position
    prev_archer_pos = archer_pos.copy()
    new_pos = archer_pos.copy()  # We'll compute the intended position

    walking = False

    if key == b'f':
        camera_mode = "fpp" if camera_mode == "tpp" else "tpp"
        aim_z_offset = 0
        glutPostRedisplay()
        return

    # Update new_pos based on keys
    if key == b'w':
        if camera_mode == "fpp" and aiming:
            aim_z_offset += aim_speed
            if aim_z_offset > 0.5:
                aim_z_offset = 0.5
        else:
            angle_rad = math.radians(archer_rotation)
            new_pos[0] -= movement_speed * math.sin(angle_rad)
            new_pos[1] += movement_speed * math.cos(angle_rad)
            walking = True

    elif key == b's':
        if camera_mode == "fpp" and aiming:
            aim_z_offset -= aim_speed
            if aim_z_offset < -0.5:
                aim_z_offset = -0.5
        else:
            angle_rad = math.radians(archer_rotation)
            new_pos[0] += movement_speed * math.sin(angle_rad)
            new_pos[1] -= movement_speed * math.cos(angle_rad)
            walking = True

    if key == b'a':
        # Rotation is independent of position updates
        archer_rotation += rotation_speed

    elif key == b'd':
        archer_rotation -= rotation_speed

    if key == b' ' and not archer_jumping:
        archer_jumping = True
        archer_jump_start_time = time.time()

    if key == b'r':
        reset_game()
        glutPostRedisplay()
        return

    # Apply field boundary constraints to new_pos
    left_platform_right = -GAP_WIDTH / 2
    left_platform_left = left_platform_right - PLATFORM_WIDTH
    right_platform_left = GAP_WIDTH / 2
    right_platform_right = right_platform_left + PLATFORM_WIDTH
    platform_front = PLATFORM_LENGTH / 2
    platform_back = -PLATFORM_LENGTH / 2

    if new_pos[0] < left_platform_left:
        new_pos[0] = left_platform_left
    elif new_pos[0] > right_platform_right:
        new_pos[0] = right_platform_right

    if new_pos[1] < platform_back:
        new_pos[1] = platform_back
    elif new_pos[1] > platform_front:
        new_pos[1] = platform_front

    # NEW: Check for obstacle collision before committing the move.
    if not is_colliding_with_obstacle(new_pos, PLAYER_COLLISION_RADIUS):
        archer_pos = new_pos
    else:
        # Optionally, print or play a sound to indicate movement is blocked.
        print("Movement blocked by an obstacle!")

    # Update the player position used for camera tracking
    player_pos[0] = archer_pos[0]
    player_pos[1] = archer_pos[1]
    player_pos[2] = archer_pos[2]

    glutPostRedisplay()



def specialKeyListener(key, x, y):
    """
    Handles special key inputs (arrow keys) for adjusting the camera angle and height.
    Only works in TPP mode.
    """
    global camera_pos, camera_angle, camera_height, game_paused
    if game_paused:
        return
    if camera_mode == "tpp":
        if key == GLUT_KEY_UP:
            camera_height += 20
        if key == GLUT_KEY_DOWN:
            camera_height -= 20
            if camera_height < 100:
                camera_height = 100
        if key == GLUT_KEY_LEFT:
            camera_angle += 5
        if key == GLUT_KEY_RIGHT:
            camera_angle -= 5
       
        rad_angle = math.radians(camera_angle)
        distance = 500
        camera_pos = (
            player_pos[0] + distance * math.sin(rad_angle),
            player_pos[1] - distance * math.cos(rad_angle),
            camera_height
        )
       
        glutPostRedisplay()


def mouseListener(button, state, x, y):
    global aiming, game_paused
    if game_over:
        glutPostRedisplay()
        return
    window_width, window_height = 1200.0, 900.0
    ui_x = x * (1000.0 / window_width)
    ui_y = (window_height - y) * (800.0 / window_height)
    
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        dx = ui_x - PAUSE_BUTTON_CENTER[0]
        dy = ui_y - PAUSE_BUTTON_CENTER[1]
        if dx*dx + dy*dy <= PAUSE_BUTTON_RADIUS**2:
            game_paused = not game_paused
            glutPostRedisplay()
            return
        
        if (abs(ui_x - QUIT_BUTTON_CENTER[0]) <= QUIT_BUTTON_SIZE / 2 and
            abs(ui_y - QUIT_BUTTON_CENTER[1]) <= QUIT_BUTTON_SIZE / 2):
            from OpenGL.GLUT import glutLeaveMainLoop
            glutLeaveMainLoop()
            return

    if button == GLUT_RIGHT_BUTTON:
        if state == GLUT_DOWN:
            aiming = True
        else:
            aiming = False
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        shoot_arrow()
    
    glutPostRedisplay()

def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, 1.25, 0.1, 3000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    if camera_mode == "fpp":
        eye_height = archer_pos[2] + ARCHER_HEIGHT * EYE_OFFSET_Z
        eye_pos = (archer_pos[0] + EYE_OFFSET_X,
                   archer_pos[1] + EYE_OFFSET_Y,
                   eye_height)
        angle_rad = math.radians(archer_rotation)
        look_dir_x = -math.sin(angle_rad)
        look_dir_y = math.cos(angle_rad)
        look_dir_z = aim_z_offset
        look_at = (eye_pos[0] + look_dir_x * 10,
                   eye_pos[1] + look_dir_y * 10,
                   eye_pos[2] + look_dir_z * 10)
        gluLookAt(
            eye_pos[0], eye_pos[1], eye_pos[2],
            look_at[0], look_at[1], look_at[2],
            0, 0, 1
        )
    else:
        gluLookAt(
            camera_pos[0], camera_pos[1], camera_pos[2],
            player_pos[0], player_pos[1], player_pos[2],
            0, 0, 1
        )


def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1,1,1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
   
    # Set up an orthographic projection that matches window coordinates
    gluOrtho2D(0, 1000, 0, 800)  # left, right, bottom, top

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
   
    # Draw text at (x, y) in screen coordinates
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
   
    # Restore original projection and modelview matrices
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)



def drawUI():
    """Draw UI elements on the screen."""
    draw_text(20, 760, f"Camera: {camera_mode.upper()}")
    draw_text(20, 730, f"Score: {player_score}")
    draw_text(20, 700, f"Balloons: {len(balloons)}/{MAX_BALLOONS}")
    draw_text(20, 670, f"Health: {player_health}%")
    draw_text(20, 640, f"Lives: {player_lives}/{MAX_LIVES}")

    if aiming:
        draw_text(20, 610, "AIMING")

    if left_platform_effect:
        draw_text(400, 760, f"WARNING: Left platform is {left_platform_effect.upper()}!")
    if right_platform_effect:
        draw_text(400, 730, f"WARNING: Right platform is {right_platform_effect.upper()}!")

    # Display hazardous balloon timers
    y_pos = 700
    for balloon_id, info in hazardous_balloons.items():
        time_left = max(0, round(info["transform_time"] - time.time()))
        draw_text(400, y_pos, f"{info['type'].upper()} balloon on {info['platform']} platform: {time_left}s until transform!")
        y_pos -= 30

    if game_over:
        draw_text(350, 450, "Your Game is Over!")
        draw_text(350, 420, f"Current score is: {player_score}.")
        draw_text(350, 390, "Press R to reset the game....")

    # Draw health bar
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glColor3f(0.7, 0.1, 0.1)  # Red background for health bar
    glBegin(GL_QUADS)
    glVertex2f(150, 670)
    glVertex2f(350, 670)
    glVertex2f(350, 685)
    glVertex2f(150, 685)
    glEnd()
    glColor3f(0.1, 0.7, 0.1)  # Green for current health
    glBegin(GL_QUADS)
    glVertex2f(150, 670)
    glVertex2f(150 + (displayed_health * 2), 670)
    glVertex2f(150 + (displayed_health * 2), 685)
    glVertex2f(150, 685)
    glEnd()
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

    draw_pause_quit_buttons()