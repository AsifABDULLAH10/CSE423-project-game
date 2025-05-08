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

if __name__ == "__main__":
    main()