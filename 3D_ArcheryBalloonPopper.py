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


def draw_crosshair():
    """Draw a crosshair/red dot for aiming in FPP mode"""
    if camera_mode == "fpp" and aiming:
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, 1000, 0, 800)
       
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
       
        glColor3f(1.0, 0.0, 0.0)
        glPointSize(5.0)
        glBegin(GL_POINTS)
        glVertex2f(500, 400)
        glEnd()
       
        glLineWidth(2.0)
        glBegin(GL_LINES)
        glVertex2f(500 - crosshair_size, 400)
        glVertex2f(500 + crosshair_size, 400)
        glVertex2f(500, 400 - crosshair_size)
        glVertex2f(500, 400 + crosshair_size)
        glEnd()
        glLineWidth(1.0)
       
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)


def shoot_arrow():
    global arrows
    if camera_mode == "fpp":
        angle_rad = math.radians(archer_rotation)
        forward_x = -math.sin(angle_rad)
        forward_y = math.cos(angle_rad)
        dir_x = forward_x
        dir_y = forward_y
        dir_z = aim_z_offset
        magnitude = math.sqrt(dir_x**2 + dir_y**2 + dir_z**2)
        dir = [dir_x/magnitude, dir_y/magnitude, dir_z/magnitude]
        start_pos = [
            archer_pos[0] + EYE_OFFSET_X,
            archer_pos[1] + EYE_OFFSET_Y,
            archer_pos[2] + ARCHER_HEIGHT * EYE_OFFSET_Z - ARROW_FIRING_OFFSET
        ]
    else:
        angle_rad = math.radians(archer_rotation)
        dir_x = -math.sin(angle_rad)
        dir_y = math.cos(angle_rad)
        dir_z = 0
        magnitude = math.sqrt(dir_x**2 + dir_y**2 + dir_z**2)
        dir = [dir_x/magnitude, dir_y/magnitude, dir_z/magnitude]
        head_radius = ARCHER_HEIGHT * 0.15
        start_pos = [
            archer_pos[0] + 30 * math.cos(angle_rad + math.pi/2),
            archer_pos[1] + 30 * math.sin(angle_rad + math.pi/2),
            archer_pos[2] + ARCHER_HEIGHT * 0.6
        ]
    
    arrow = {
        "pos": start_pos.copy() if isinstance(start_pos, list) else list(start_pos),
        "dir": dir,
        "start_time": time.time()
    }
    arrows.append(arrow)


def update_arrows():
    """Update positions of all active arrows and remove expired ones"""
    global arrows, power_up_active
    current_time = time.time()
    keep_arrows = []
    speed_multiplier = 1.5 if power_up_active == "yellow" else 1.0

    for arrow in arrows:
        start_time = arrow["start_time"]
        if current_time - start_time > ARROW_LIFETIME:
            continue
        pos = arrow["pos"]
        dir = arrow["dir"]
        pos[0] += dir[0] * ARROW_SPEED * speed_multiplier
        pos[1] += dir[1] * ARROW_SPEED * speed_multiplier
        pos[2] += dir[2] * ARROW_SPEED * speed_multiplier
        keep_arrows.append(arrow)
    arrows = keep_arrows


def draw_arrow(pos, dir, length=50):
    """Draw an arrow at the given position, pointing in the given direction"""
    glPushMatrix()
   
    # Position the arrow
    glTranslatef(pos[0], pos[1], pos[2])
   
    # Calculate rotation angles to align with direction
   
    # Normalize direction vector to be safe
    magnitude = math.sqrt(dir[0]**2 + dir[1]**2 + dir[2]**2)
    if magnitude > 0:
        dir = [d/magnitude for d in dir]
   
    # Calculate rotation to align arrow with direction
    if abs(dir[2] - 1.0) < 0.001:
        rotation_angle = 0
        rotation_axis = [1, 0, 0]
    elif abs(dir[2] + 1.0) < 0.001:
        rotation_angle = 180
        rotation_axis = [1, 0, 0]
    else:
        z_axis = [0, 0, 1]
        rotation_axis = [
            dir[1] * z_axis[2] - dir[2] * z_axis[1],
            dir[2] * z_axis[0] - dir[0] * z_axis[2],
            dir[0] * z_axis[1] - dir[1] * z_axis[0]
        ]
       
        axis_mag = math.sqrt(sum(v*v for v in rotation_axis))
        if axis_mag > 0:
            rotation_axis = [v/axis_mag for v in rotation_axis]
           
        dot_product = dir[0] * z_axis[0] + dir[1] * z_axis[1] + dir[2] * z_axis[2]
        rotation_angle = math.degrees(math.acos(max(-1.0, min(1.0, dot_product))))
   
    if rotation_angle != 0:
        glRotatef(rotation_angle, rotation_axis[0], rotation_axis[1], rotation_axis[2])
   
    quadric = gluNewQuadric()
    gluQuadricNormals(quadric, GLU_SMOOTH)
   
    glColor3f(0.8, 0.2, 0.2)
    glPushMatrix()
    glRotatef(180, 1, 0, 0)
    gluCylinder(quadric, 3.0, 0.0, 10.0, 8, 1)
    glPopMatrix()
   
    glColor3f(0.6, 0.3, 0.1)
    gluCylinder(quadric, 1.0, 1.0, length, 8, 1)
   
    glTranslatef(0, 0, length)
    glColor3f(0.1, 0.1, 0.1)
    gluDisk(quadric, 0, 1.5, 8, 1)
    gluCylinder(quadric, 1.5, 1.5, 3.0, 8, 1)
   
    gluDeleteQuadric(quadric)
    glPopMatrix()


def check_arrow_balloon_collisions():
    """Check for collisions between arrows and balloons, handling power-up and golden balloons."""
    global arrows, balloons, player_score, normal_balloons_popped_count, balloons_popped_total
    global power_up_active, power_up_end_time, golden_balloon_notification, hazardous_balloons

    arrows_to_remove = []
    balloons_to_remove = []
    current_time = time.time()

    for arrow_idx, arrow in enumerate(arrows):
        for balloon_idx, balloon in enumerate(balloons):
            dx = arrow["pos"][0] - balloon["pos"][0]
            dy = arrow["pos"][1] - balloon["pos"][1]
            dz = arrow["pos"][2] - balloon["pos"][2]
            distance = math.sqrt(dx * dx + dy * dy + dz * dz)
            if distance < balloon["radius"] + 5:
                # Handle purple (hazardous) balloons first
                if balloon["color_type"] == "purple":
                    if balloon["id"] in hazardous_balloons:
                        hazardous_balloons.pop(balloon["id"], None)
                    balloons_to_remove.append(balloon_idx)
                    arrows_to_remove.append(arrow_idx)
                    continue

                # For normal balloons that give points ("grey", "black", "blue")
                if balloon["color_type"] in ["grey", "black", "blue"]:
                    player_score += balloon["points"]
                    balloons_popped_total += 1
                    normal_balloons_popped_count += 1
                    # When 5 normal balloons have been popped, spawn a power-up balloon
                    if normal_balloons_popped_count >= 5:
                        spawn_powerup_balloon()
                        normal_balloons_popped_count = 0
                    # Also check for golden balloon condition
                    if balloons_popped_total >= GOLDEN_THRESHOLD:
                        spawn_golden_balloon()
                        balloons_popped_total = 0

                    balloons_to_remove.append(balloon_idx)
                    arrows_to_remove.append(arrow_idx)

                # For balloons with additional effects (health boost and extra life)
                elif balloon["color_type"] in ["light_green", "red"]:
                    apply_balloon_effect(balloon)
                    check_score_rewards()
                    balloons_to_remove.append(balloon_idx)
                    arrows_to_remove.append(arrow_idx)

                # For power-up balloons (yellow, brown) that were spawned earlier
                elif balloon["color_type"] in ["yellow", "brown"]:
                    if balloon["color_type"] == "yellow":
                        power_up_active = "yellow"  # Faster arrows effect.
                    else:
                        power_up_active = "brown"   # Slow-motion balloons effect.
                    power_up_end_time = time.time() + POWERUP_LIFETIME
                    print("Power-up activated:", power_up_active)
                    balloons_to_remove.append(balloon_idx)
                    arrows_to_remove.append(arrow_idx)

                # For golden balloon
                elif balloon["color_type"] == "golden":
                    bonus_score = 0
                    for b in balloons:
                        if b["color_type"] == "grey":
                            bonus_score += 5
                        elif b["color_type"] == "black":
                            bonus_score += 10
                        elif b["color_type"] == "blue":
                            bonus_score += 20
                    player_score += bonus_score + 100
                    balloons = []
                    golden_balloon_notification = ""
                    arrows_to_remove.append(arrow_idx)

    # Remove collided balloons and arrows in reverse order to avoid index issues
    for idx in sorted(balloons_to_remove, reverse=True):
        if idx < len(balloons):
            balloons.pop(idx)
    for idx in sorted(arrows_to_remove, reverse=True):
        if idx < len(arrows):
            arrows.pop(idx)



def update_health_bar():
    """for the displayed health value toward the actual player_health."""
    global displayed_health, player_health
    diff = player_health - displayed_health
    # (0.1) so rather than overshooting the bar updates gradually .
    displayed_health += diff * 0.1
    # displayed_health to not go below 0.
    if displayed_health < 0:
        displayed_health = 0


def check_balloon_player_collisions():
    """Check for collisions between balloons and the player"""
    global balloons, player_health, player_lives, game_over
    
    balloons_to_remove = []
    
    # Player dimensions for better collision detection
    player_width = ARCHER_HEIGHT * 0.3  # Approximate width of the player
    player_height = ARCHER_HEIGHT  # Full height of the player
    
    # For each balloon
    for balloon_idx, balloon in enumerate(balloons):
        # Calculate horizontal distance (x-y plane)
        dx = balloon["pos"][0] - archer_pos[0]
        dy = balloon["pos"][1] - archer_pos[1]
        horizontal_distance = math.sqrt(dx*dx + dy*dy)
        
        # Calculate vertical distance (z-axis)
        dz = abs(balloon["pos"][2] - (archer_pos[2] + player_height/2))
        
        # Collision occurs if:
        # 1. Horizontal distance is less than player_width + balloon_radius
        # 2. Vertical distance is less than player_height/2 + balloon_radius
        if (horizontal_distance < (player_width + balloon["radius"]) and 
            dz < (player_height/2 + balloon["radius"])):
            
            # Balloon collided with player
            print(f"Collision detected! Health reduced from {player_health} to {player_health-10}")
            
            # Reduce player health by 10%
            player_health -= 10
            
            # Mark balloon for removal (popping)
            if balloon_idx not in balloons_to_remove:
                balloons_to_remove.append(balloon_idx)
            
            # Check if health is depleted
            if player_health <= 0:
                player_lives -= 1
                player_health = 100  # Reset health
                
                # Check if all lives are lost
                if player_lives <= 0:
                    game_over = True
    
    # Remove collided balloons (in reverse order to avoid index issues)
    for idx in sorted(balloons_to_remove, reverse=True):
        if idx < len(balloons):
            balloons.pop(idx)



def check_obstacle_collision(new_pos):
    """
    Returns True if new_pos collides with any obstacle.
    Using a simple radius check on the xy-plane.
    """
    for obs in obstacles:
        dx = new_pos[0] - obs["pos"][0]
        dy = new_pos[1] - obs["pos"][1]
        distance = math.sqrt(dx * dx + dy * dy)
        if distance < (obs["radius"] + PLAYER_COLLISION_RADIUS):
            return True
    return False


def is_colliding_with_obstacle(pos, obj_radius):
    """
    Returns True if the given position (pos: [x, y, _]) collides with any obstacle's area.
    Uses a radius test on the X-Y plane.
    """
    for obs in obstacles:
        dx = pos[0] - obs["pos"][0]
        dy = pos[1] - obs["pos"][1]
        distance = math.sqrt(dx*dx + dy*dy)
        if distance < (obj_radius + obs["radius"]):
            return True
    return False


def apply_balloon_effect(balloon):
    """Apply effects based on the balloon color"""
    global player_health, player_lives, left_platform_effect, right_platform_effect
    global left_platform_effect_start_time, right_platform_effect_start_time, hazardous_balloons
    
    color_type = balloon["color_type"]
    
    # Light green balloon - health boost
    if color_type == "light_green":
        if player_health < 100:
            player_health = min(100, player_health + 25)
            print(f"Health boost! Health increased to {player_health}%")
    
    # Red balloon - extra life
    elif color_type == "red":
        if player_lives < MAX_LIVES:
            player_lives += 1
            print(f"Extra life gained! Lives: {player_lives}")
    
    # Remove from hazardous tracking if it was a lava or poison balloon
    if balloon["id"] in hazardous_balloons:
        del hazardous_balloons[balloon["id"]]



def check_score_rewards():
    """Check if player has earned any rewards based on score"""
    global player_score, player_lives

    # Award an extra life for every 500 points, up to maximum
    lives_earned = min(player_score // 500, MAX_LIVES)
    if lives_earned > player_lives - 5:  # Original lives were 5
        # Player earned a new life
        new_lives = 5 + lives_earned
        if new_lives > player_lives:
            player_lives = min(new_lives, MAX_LIVES)


def check_game_over():
    global game_over
    # Game over if 40 or more balloons, or if both health and lives are exhausted.
    if len(balloons) >= 40 or (player_health <= 0 and player_lives <= 0):
        game_over = True


def draw_platform(x, y, z, width, length, thickness, color=None):
    """Draw a platform at the specified position with given dimensions"""
    glPushMatrix()
    glTranslatef(x, y, z)
   
    if color is None:
        color = (0.2, 0.7, 0.3)  # Default green color
   
    # Draw the platform (a flat cuboid)
    glBegin(GL_QUADS)
    # Top face
    glColor3f(color[0], color[1], color[2])  # Main color for platform surface
    glVertex3f(-width/2, -length/2, thickness/2)
    glVertex3f(width/2, -length/2, thickness/2)
    glVertex3f(width/2, length/2, thickness/2)
    glVertex3f(-width/2, length/2, thickness/2)
   
    # Bottom face
    glColor3f(color[0]*0.75, color[1]*0.75, color[2]*0.75)  # Darker color for bottom
    glVertex3f(-width/2, -length/2, -thickness/2)
    glVertex3f(width/2, -length/2, -thickness/2)
    glVertex3f(width/2, length/2, -thickness/2)
    glVertex3f(-width/2, length/2, -thickness/2)
   
    # Side faces
    glColor3f(color[0]*0.9, color[1]*0.9, color[2]*0.9)  # Medium shade for sides
    # Front
    glVertex3f(-width/2, -length/2, thickness/2)
    glVertex3f(width/2, -length/2, thickness/2)
    glVertex3f(width/2, -length/2, -thickness/2)
    glVertex3f(-width/2, -length/2, -thickness/2)
   
    # Back
    glVertex3f(-width/2, length/2, thickness/2)
    glVertex3f(width/2, length/2, thickness/2)
    glVertex3f(width/2, length/2, -thickness/2)
    glVertex3f(-width/2, length/2, -thickness/2)
   
    # Left
    glVertex3f(-width/2, -length/2, thickness/2)
    glVertex3f(-width/2, length/2, thickness/2)
    glVertex3f(-width/2, length/2, -thickness/2)
    glVertex3f(-width/2, -length/2, -thickness/2)
   
    # Right
    glVertex3f(width/2, -length/2, thickness/2)
    glVertex3f(width/2, length/2, thickness/2)
    glVertex3f(width/2, length/2, -thickness/2)
    glVertex3f(width/2, -length/2, -thickness/2)
    glEnd()
   
    glPopMatrix()



def draw_edge_line():
    """Draw the connecting edge line between the two platforms"""
    glPushMatrix()
   
    # Position the edge line between the two platforms
    glTranslatef(0, 0, PLATFORM_HEIGHT)
   
    # Draw the edge line as a thin rectangle
    glBegin(GL_QUADS)
    # Top face
    glColor3f(1.0, 1.0, 1.0)  # White color for the edge line
    glVertex3f(-GAP_WIDTH/2, -PLATFORM_LENGTH/2, PLATFORM_THICKNESS/2 + 1)
    glVertex3f(GAP_WIDTH/2, -PLATFORM_LENGTH/2, PLATFORM_THICKNESS/2 + 1)
    glVertex3f(GAP_WIDTH/2, PLATFORM_LENGTH/2, PLATFORM_THICKNESS/2 + 1)
    glVertex3f(-GAP_WIDTH/2, PLATFORM_LENGTH/2, PLATFORM_THICKNESS/2 + 1)
    glEnd()
   
    glPopMatrix()



def spawn_obstacles():
    """Spawn trees and bushes on the field."""
    global obstacles
    obstacles = []

    # Determine boundaries using platform dimensions.
    left_platform_right = -GAP_WIDTH / 2
    left_platform_left = left_platform_right - PLATFORM_WIDTH
    right_platform_left = GAP_WIDTH / 2
    right_platform_right = right_platform_left + PLATFORM_WIDTH
    platform_front = PLATFORM_LENGTH / 2
    platform_back = -PLATFORM_LENGTH / 2

    # Spawn trees
    for i in range(TREE_OBSTACLE_COUNT):
        tree = {
            "type": "tree",
            "pos": [
                random.uniform(left_platform_left + 50, right_platform_right - 50),
                random.uniform(platform_back + 50, platform_front - 50),
                PLATFORM_HEIGHT + PLATFORM_THICKNESS/2  # On the field
            ],
            "height": TREE_HEIGHT,   # Twice the player's height
            "radius": TREE_RADIUS    # (used for collision checks)
        }
        obstacles.append(tree)
    # Spawn bushes
    for i in range(BUSH_OBSTACLE_COUNT):
        bush = {
            "type": "bush",
            "pos": [
                random.uniform(left_platform_left + 50, right_platform_right - 50),
                random.uniform(platform_back + 50, platform_front - 50),
                PLATFORM_HEIGHT + PLATFORM_THICKNESS/2  # On the field
            ],
            "height": BUSH_HEIGHT,   # Half the player's height
            "radius": BUSH_RADIUS    # (used for collision checks)
        }
        obstacles.append(bush)


def draw_obstacles():
    """Draw trees and bushes on the field with updated sizes and dark-green colors."""
    for obs in obstacles:
        glPushMatrix()
        glTranslatef(obs["pos"][0], obs["pos"][1], obs["pos"][2])
        if obs["type"] == "tree":
            # Draw tree: trunk occupies 40% of tree height.
            trunk_height = obs["height"] * 0.4
            trunk_radius = 8  # You may adjust this as needed.
            glColor3f(0.55, 0.27, 0.07)  # Brown trunk color.
            quad = gluNewQuadric()
            gluCylinder(quad, trunk_radius, trunk_radius, trunk_height, 12, 12)
            glTranslatef(0, 0, trunk_height)
            # Draw canopy as a cone: 60% of the tree's height.
            canopy_height = obs["height"] * 0.6
            canopy_radius = obs["height"] * 0.3
            glColor3f(*TREE_COLOR)  # Dark green canopy.
            glutSolidCone(canopy_radius, canopy_height, 12, 12)
            gluDeleteQuadric(quad)
        elif obs["type"] == "bush":
            # Draw bush as a sphere with a diameter equal to BUSH_HEIGHT.
            glColor3f(*BUSH_COLOR)  # Dark green bush.
            glutSolidSphere(obs["height"] * 0.5, 12, 12)
        glPopMatrix()



def spawn_balloon():
    """Spawn a new balloon at a random position in the field"""
    global balloons, hazardous_balloons
    
    # balloon spawn stop
    if game_over:
        return
    
    # random platform
    on_left_platform = random.choice([True, False])
    platform_side = "left" if on_left_platform else "right"
    
    if on_left_platform:

        x_min = -(PLATFORM_WIDTH + GAP_WIDTH/2)
        x_max = -GAP_WIDTH/2
    else:

        x_min = GAP_WIDTH/2
        x_max = PLATFORM_WIDTH + GAP_WIDTH/2
    
    # Random position on the platform
    x = random.uniform(x_min, x_max)
    y = random.uniform(-PLATFORM_LENGTH/2, PLATFORM_LENGTH/2)
    
    # the balloon is not too close to the archer
    distance_to_archer = math.sqrt((x - archer_pos[0])**2 + (y - archer_pos[1])**2)
    if distance_to_archer < 100:
        return
    
    # Z position
    z = PLATFORM_HEIGHT + PLATFORM_THICKNESS/2 + random.uniform(50, 250)
    
    # balloon color based on probability
    color_type = select_balloon_color()
    color_info = BALLOON_COLORS[color_type]
    
    # movement vector
    movement_angle = random.uniform(0, 2 * math.pi)
    movement_dir = [
        math.cos(movement_angle) * BALLOON_SPEED,
        math.sin(movement_angle) * BALLOON_SPEED,
        0  # 0 movement for z-axis
    ]
    
    # unique ID for the balloon
    balloon_id = len(balloons) + random.randint(1000, 9999)
    
    # Create balloon object
    balloon = {
        "id": balloon_id,
        "pos": [x, y, z],
        "radius": 20,  # Balloon radius
        "color_type": color_type,
        "color": color_info["color"],
        "points": color_info["points"],
        "movement_dir": movement_dir,
        "platform": platform_side,
        "spawn_time": time.time()
    }
    
    # for tracking hazardous balloons 
    if color_type in ["lava", "purple"]:
        hazardous_balloons[balloon_id] = {
            "type": color_type,
            "spawn_time": time.time(),
            "platform": platform_side,
            "transform_time": time.time() + 20.0  # platform transform
        }
    
    # balloons list
    balloons.append(balloon)


def spawn_powerup_balloon():
    """
    Spawn a power-up balloon. Randomly pick between:
      - "yellow": for faster arrows (arrow speed ×1.5 when popped)
      - "brown": for slow-motion balloons (balloon movement ×0.5 when popped)
    The power-up balloon will disappear from the field after 20 seconds if not popped.
    """
    global balloons
    # Choose power-up type randomly.
    powerup_type = random.choice(["yellow", "brown"])
    if powerup_type == "yellow":
        color = (1.0, 1.0, 0.0)  # Yellow
    else:  # "brown"
        color = (0.6, 0.4, 0.2)  # Brown

    # Select a platform as in spawn_balloon()
    on_left_platform = random.choice([True, False])
    platform_side = "left" if on_left_platform else "right"
    if on_left_platform:
        x_min = -(PLATFORM_WIDTH + GAP_WIDTH/2)
        x_max = -GAP_WIDTH/2
    else:
        x_min = GAP_WIDTH/2
        x_max = PLATFORM_WIDTH + GAP_WIDTH/2
    # Random x and y positions on the chosen platform
    x = random.uniform(x_min, x_max)
    y = random.uniform(-PLATFORM_LENGTH/2, PLATFORM_LENGTH/2)
    # Ensure a minimum distance from the archer
    if math.sqrt((x - archer_pos[0])**2 + (y - archer_pos[1])**2) < 100:
        x += 100
        y += 100

    # Set z slightly above the platform surface.
    z = PLATFORM_HEIGHT + PLATFORM_THICKNESS/2 + random.uniform(50, 250)

    # Create a movement vector in the x-y plane
    movement_angle = random.uniform(0, 2 * math.pi)
    movement_dir = [
        math.cos(movement_angle) * BALLOON_SPEED,
        math.sin(movement_angle) * BALLOON_SPEED,
        0
    ]

    balloon_id = len(balloons) + random.randint(1000, 9999)

    powerup_balloon = {
        "id": balloon_id,
        "pos": [x, y, z],
        "radius": 20,
        "color_type": powerup_type,  # "yellow" or "brown"
        "color": color,
        "points": 0,  # No score boost
        "movement_dir": movement_dir,
        "platform": platform_side,
        "spawn_time": time.time()  # To track its 20-sec lifetime
    }
    balloons.append(powerup_balloon)



def spawn_golden_balloon():
    """
    Spawns a Golden Balloon that stays in the field for GOLDEN_LIFETIME seconds.
    When spawned, it sets a notification message.
    """
    global balloons, golden_balloon_notification
    # Set notification so that your UI can display it.
    golden_balloon_notification = "Golden Balloon Spawned! Pop it for bonus!"
    
    # Choose a random platform (similar to other balloon spawning).
    on_left_platform = random.choice([True, False])
    platform_side = "left" if on_left_platform else "right"
    if on_left_platform:
        x_min = -(PLATFORM_WIDTH + GAP_WIDTH/2)
        x_max = -GAP_WIDTH/2
    else:
        x_min = GAP_WIDTH/2
        x_max = PLATFORM_WIDTH + GAP_WIDTH/2

    x = random.uniform(x_min, x_max)
    y = random.uniform(-PLATFORM_LENGTH/2, PLATFORM_LENGTH/2)
    # Ensure minimum distance from archer.
    if math.sqrt((x - archer_pos[0])**2 + (y - archer_pos[1])**2) < 100:
        x += 100
        y += 100

    z = PLATFORM_HEIGHT + PLATFORM_THICKNESS/2 + random.uniform(50, 250)
    movement_angle = random.uniform(0, 2 * math.pi)
    movement_dir = [
        math.cos(movement_angle) * BALLOON_SPEED,
        math.sin(movement_angle) * BALLOON_SPEED,
        0
    ]
    balloon_id = len(balloons) + random.randint(1000, 9999)
    
    golden_balloon = {
        "id": balloon_id,
        "pos": [x, y, z],
        "radius": 20,
        "color_type": "golden",
        "color": (1.0, 0.84, 0.0),  # A gold-like color.
        "points": 0,  # It gives no immediate score.
        "movement_dir": movement_dir,
        "platform": platform_side,
        "spawn_time": time.time()  # Used to determine lifetime.
    }
    balloons.append(golden_balloon)


def select_balloon_color():
    """Select a balloon color based on probabilities"""
    rand_value = random.random()
    cumulative_prob = 0
    
    for color_type, info in BALLOON_COLORS.items():
        cumulative_prob += info["probability"]
        if rand_value < cumulative_prob:
            return color_type
    
    # Fallback to grey if something goes wrong
    return "grey"



def update_balloons():
    """Update positions of all balloons and handle boundary collisions."""
    global balloons, power_up_active
    current_time = time.time()
    move_multiplier = 0.5 if power_up_active == "brown" else 1.0

    for balloon in balloons[:]:
        # Remove golden balloons if they exceeded lifetime.
        if balloon["color_type"] == "golden" and (current_time - balloon["spawn_time"]) > GOLDEN_LIFETIME:
            balloons.remove(balloon)
            golden_balloon_notification = ""  # Clear notification when expired.
            continue
        new_x = balloon["pos"][0] + balloon["movement_dir"][0] * move_multiplier
        new_y = balloon["pos"][1] + balloon["movement_dir"][1] * move_multiplier
        new_pos = [new_x, new_y, balloon["pos"][2]]
        # If the new position would intersect an obstacle, reverse direction
        if is_colliding_with_obstacle(new_pos, balloon["radius"]):
            balloon["movement_dir"][0] *= -1
            balloon["movement_dir"][1] *= -1
        else:
            balloon["pos"][0] = new_x
            balloon["pos"][1] = new_y

        # Update balloon positions.
        balloon["pos"][0] += balloon["movement_dir"][0] * move_multiplier
        balloon["pos"][1] += balloon["movement_dir"][1] * move_multiplier
        # (Boundary collision handling code remains unchanged below.)
        if balloon["pos"][0] < -(PLATFORM_WIDTH + GAP_WIDTH/2):
            balloon["pos"][0] = -(PLATFORM_WIDTH + GAP_WIDTH/2)
            balloon["movement_dir"][0] *= -1
        elif balloon["pos"][0] > (PLATFORM_WIDTH + GAP_WIDTH/2):
            balloon["pos"][0] = (PLATFORM_WIDTH + GAP_WIDTH/2)
            balloon["movement_dir"][0] *= -1

        if balloon["pos"][1] < -PLATFORM_LENGTH/2:
            balloon["pos"][1] = -PLATFORM_LENGTH/2
            balloon["movement_dir"][1] *= -1
        elif balloon["pos"][1] > PLATFORM_LENGTH/2:
            balloon["pos"][1] = PLATFORM_LENGTH/2
            balloon["movement_dir"][1] *= -1


def draw_balloons():
    """Draw all active balloons."""
    for balloon in balloons:
        glPushMatrix()
        # Position at balloon location
        glTranslatef(balloon["pos"][0], balloon["pos"][1], balloon["pos"][2])
        # Set balloon color
        glColor3f(balloon["color"][0], balloon["color"][1], balloon["color"][2])
        # Draw balloon (sphere)
        glutSolidSphere(balloon["radius"], 16, 16)
        # Draw string: a line downward from balloon bottom
        glColor3f(0.9, 0.9, 0.9)
        glLineWidth(1.0)
        glBegin(GL_LINES)
        glVertex3f(0, 0, 0)
        glVertex3f(0, 0, -100)
        glEnd()
        glPopMatrix()



def update_platform_effects():
    """Update platform effects and check for timed transformations."""
    global hazardous_balloons, left_platform_effect, right_platform_effect
    global left_platform_effect_start_time, right_platform_effect_start_time
    global player_health, last_effect_damage_time, player_lives, game_over

    current_time = time.time()

    # Check hazardous balloons for transformation
    balloons_to_remove = []
    for balloon_id, info in list(hazardous_balloons.items()):
        if current_time >= info["transform_time"]:
            # Transform the platform the balloon was last on.
            if info["platform"] == "left":
                if info["type"] in ["lava", "purple"]:  # Handles both lava and purple effects
                    left_platform_effect = info["type"]  # Directly set to "lava" or "purple"
                    left_platform_effect_start_time = current_time
                    print(f"LEFT PLATFORM TRANSFORMED TO {left_platform_effect.upper()}!")
            elif info["platform"] == "right":
                if info["type"] in ["lava", "purple"]:
                    right_platform_effect = info["type"]
                    right_platform_effect_start_time = current_time
                    print(f"RIGHT PLATFORM TRANSFORMED TO {right_platform_effect.upper()}!")
            balloons_to_remove.append(balloon_id)

            # Remove the balloon from the game list.
            for i, balloon in enumerate(balloons):
                if balloon["id"] == balloon_id:
                    balloons.pop(i)
                    break

    for balloon_id in balloons_to_remove:
        hazardous_balloons.pop(balloon_id, None)

    # Expiration of platform transformation
    if left_platform_effect and current_time > left_platform_effect_start_time + platform_effect_duration:
        left_platform_effect = None
        print("Left platform effect expired")
    if right_platform_effect and current_time > right_platform_effect_start_time + platform_effect_duration:
        right_platform_effect = None
        print("Right platform effect expired")

    # Apply damage if player is standing on affected platform (lava or purple)
    if current_time - last_effect_damage_time >= effect_damage_interval:
        is_on_left = archer_pos[0] < 0
        effect_active = (left_platform_effect if is_on_left else right_platform_effect)

        if effect_active in ["lava", "purple"]:
            player_health -= 20
            last_effect_damage_time = current_time
            print(f"Platform damage! Health reduced to {player_health}%")
            
            if player_health <= 0:
                player_lives -= 1
                if player_lives > 0:
                    player_health = 100  # Reset health since a life was lost
                    print("Life lost! Health reset to 100.")
                else:
                    game_over = True
                    print("Game Over!")


def spawn_clouds():
    """Spawn clouds around the field with a long, curvy appearance."""
    global clouds
    clouds = []
    
    field_radius = max(PLATFORM_WIDTH/2 + GAP_WIDTH, PLATFORM_LENGTH/2) + CLOUD_MARGIN
    
    for i in range(NUM_CLOUDS):
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(field_radius * 0.8, field_radius)
        x = distance * math.cos(angle)
        y = distance * math.sin(angle)
        z = random.uniform(CLOUD_MIN_Z, CLOUD_MAX_Z)
        scale_factors = [random.uniform(4.0, 6.0), random.uniform(1.0, 2.0), random.uniform(1.2, 3.0)]
        clouds.append({
            "pos": [x, y, z],
            "scale": scale_factors
        })


def draw_clouds():
    """Draw clouds as elongated, curvy white shapes in the sky."""
    glColor3f(1.0, 1.0, 1.0)
    for cloud in clouds:
        glPushMatrix()
        glTranslatef(cloud["pos"][0], cloud["pos"][1], cloud["pos"][2])
        glScalef(cloud["scale"][0], cloud["scale"][1], cloud["scale"][2])
        glutSolidSphere(30, 12, 12)
        glPopMatrix()


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
    



def draw_pause_quit_buttons():
    """
    Draw the pause/resume icon and quit button without any surrounding background.
    The pause/resume icon is scaled to fit in a square of size QUIT_BUTTON_SIZE,
    making it equivalent in size to the exit (quit) button.
    """
    # Use QUIT_BUTTON_SIZE as the icon size for the pause/resume button.
    icon_size = QUIT_BUTTON_SIZE  # e.g., 30
    half_size = icon_size / 2.0

    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)  # Set up orthographic window coordinates
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    # Draw the pause/resume icon at PAUSE_BUTTON_CENTER.
    cx, cy = PAUSE_BUTTON_CENTER
    glColor3f(0.0, 0.0, 0.0)  # Icon color: black.
    if game_paused:
        # When the game is paused, display a right-facing triangle (play icon).
        # The triangle is drawn to fit in a square of size 'icon_size'.
        glBegin(GL_POLYGON)
        glVertex2f(cx - half_size, cy - half_size)  # Left-bottom
        glVertex2f(cx - half_size, cy + half_size)  # Left-top
        glVertex2f(cx + half_size, cy)              # Right-middle
        glEnd()
    else:
        # When the game is running (not paused), display two vertical bars (pause icon).
        # Define dimensions relative to 'icon_size' so that the overall width fits.
        bar_width = icon_size * 0.3      # Each bar's width is 30% of icon_size.
        gap = icon_size * 0.1            # Gap between the two bars (10% of icon_size).
        bar_height = icon_size           # Height equals icon_size.
        total_width = 2 * bar_width + gap
        x_offset = total_width / 2.0     # Used to center the two bars horizontally.

        # Calculate left bar coordinates.
        left_bar_left = cx - x_offset
        left_bar_right = left_bar_left + bar_width
        # Calculate right bar coordinates.
        right_bar_left = left_bar_left + bar_width + gap
        right_bar_right = right_bar_left + bar_width

        top_y = cy + bar_height / 2.0
        bottom_y = cy - bar_height / 2.0

        # Draw left vertical bar.
        glBegin(GL_QUADS)
        glVertex2f(left_bar_left, bottom_y)
        glVertex2f(left_bar_right, bottom_y)
        glVertex2f(left_bar_right, top_y)
        glVertex2f(left_bar_left, top_y)
        glEnd()
        # Draw right vertical bar.
        glBegin(GL_QUADS)
        glVertex2f(right_bar_left, bottom_y)
        glVertex2f(right_bar_right, bottom_y)
        glVertex2f(right_bar_right, top_y)
        glVertex2f(right_bar_left, top_y)
        glEnd()

    # Draw the quit button as a red "X", using QUIT_BUTTON_SIZE.
    glColor3f(1.0, 0.0, 0.0)
    qx, qy = QUIT_BUTTON_CENTER
    s = QUIT_BUTTON_SIZE / 2.0
    glLineWidth(3.0)
    glBegin(GL_LINES)
    glVertex2f(qx - s, qy - s)
    glVertex2f(qx + s, qy + s)
    glVertex2f(qx - s, qy + s)
    glVertex2f(qx + s, qy - s)
    glEnd()
    glLineWidth(1.0)

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)



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




def idle():
    """ power-up expiration.archer physics and leg animation.arrow and balloon positions
        new balloons at set intervals.
        Checks for collisions.
        Updates platform effects.
        Updates the health bar.
        Triggers a screen redraw.
    """
    global power_up_active, power_up_end_time, last_balloon_spawn_time, walking, game_paused, game_over
    if game_over:
        glutPostRedisplay()
        return
    if game_paused:
        glutPostRedisplay()
        return
    if power_up_active is not None and time.time() >= power_up_end_time:
        print("Power-up expired:", power_up_active)
        power_up_active = None

    prev_pos = archer_pos.copy()

    update_archer_physics()

    if not walking and not archer_jumping:
        update_leg_animation()
    elif walking:
        update_leg_animation()

    update_arrows()

    current_time = time.time()
    if current_time - last_balloon_spawn_time >= BALLOON_SPAWN_INTERVAL and not game_over:
        spawn_balloon()
        last_balloon_spawn_time = current_time

    update_balloons()

    check_arrow_balloon_collisions()

    check_balloon_player_collisions()

    update_platform_effects()

    check_game_over()

    update_health_bar()

    glutPostRedisplay()



def showScreen():
    """
    Display function to render the scene and all game elements.
    """
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    setupCamera()
    # The call to setupLighting() has been removed.
    drawEnvironment()
    if camera_mode != "fpp":
        draw_humanoid()
    for arrow in arrows:
        draw_arrow(arrow["pos"], arrow["dir"])
    draw_balloons()
    draw_crosshair()
    drawUI()
    glutSwapBuffers()



def drawEnvironment():
    # Determine platform colors based on effect status
    left_color = (0.2, 0.4, 0.8)  # Default blue
    if left_platform_effect == "lava":
        left_color = (0.9, 0.4, 0.1)  # Lava orange
    elif left_platform_effect in ["poison", "purple"]:
        left_color = (0.7, 0.3, 0.9)  # Purple (or poison) effect

    right_color = (0.2, 0.7, 0.3)  # Default green
    if right_platform_effect == "lava":
        right_color = (0.9, 0.4, 0.1)  # Lava orange
    elif right_platform_effect in ["poison", "purple"]:
        right_color = (0.7, 0.3, 0.9)  # Purple (or poison) effect

    # Draw platforms with updated colors:
    draw_platform(
        -(PLATFORM_WIDTH/2 + GAP_WIDTH/2), 0, PLATFORM_HEIGHT,
        PLATFORM_WIDTH, PLATFORM_LENGTH, PLATFORM_THICKNESS,
        left_color
    )

    draw_platform(
        (PLATFORM_WIDTH/2 + GAP_WIDTH/2), 0, PLATFORM_HEIGHT,
        PLATFORM_WIDTH, PLATFORM_LENGTH, PLATFORM_THICKNESS,
        right_color
    )

    # Draw the white edge line, obstacles, and clouds
    draw_edge_line()
    draw_obstacles()
    draw_clouds()




def initGL():
    # we simply set the background color.
    glClearColor(0.8, 1.0, 0.8, 1.0)



def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1200, 900)
    glutInitWindowPosition(50, 50)
    glutCreateWindow(b"3D Archer Game")
    glutDisplayFunc(showScreen)
    glutIdleFunc(idle)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    initGL()
    spawn_clouds()
    spawn_obstacles()
    glutMainLoop()


if __name__ == "__main__":
    main()
