
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
    # Use proper 3D rotations to orient the arrow
   
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