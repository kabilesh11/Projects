import cv2
import numpy as np
import time
import random
import os

CANVAS_WIDTH = 800
CANVAS_HEIGHT = 550

BACKGROUND_IMAGE_PATH = 'intersection_background.jpg' 
CAR_SPRITE_DIR = 'car_sprites/'

ROAD_WIDTH = 180
LANE_WIDTH = ROAD_WIDTH / 2

CAR_RENDER_SIZE_MIN = 30
CAR_RENDER_SIZE_MAX = 50
CAR_SPEED_MIN = 6
CAR_SPEED_MAX = 10
MAX_CARS_PER_ROAD = 10
SPAWN_INTERVAL_FRAMES = 10
# Traffic signal parameters
MIN_GREEN_TIME_SEC = 3
MAX_GREEN_TIME_SEC = 8 # Slightly reduced max green time
YELLOW_TIME_SEC = 2
RED_TRANSITION_TIME_SEC = 0.5

# Traffic analysis parameters
MIN_QUEUE_TO_SWITCH = 1 # More responsive to small queues
NO_QUEUE_THRESHOLD = 0

NS_STOP_LINE_OFFSET = ROAD_WIDTH // 2 + 25 
EW_STOP_LINE_OFFSET = ROAD_WIDTH // 2 + 25 

# --- Global Simulation State ---
ns_cars = []
ew_cars = []

current_signal = 'NS'
signal_state = 'GREEN'
signal_timer_start_time = time.time()

# --- Global Image Assets ---
background_img = None
car_sprites = {}

# --- Helper function to overlay PNG with alpha channel ---
def overlay_alpha_image(background, foreground, x_offset, y_offset):
    # Ensure offsets are integers
    x_offset = int(x_offset)
    y_offset = int(y_offset)

    # Get dimensions of foreground (car sprite)
    fg_height, fg_width, _ = foreground.shape

    y1_bg = max(0, y_offset)
    y2_bg = min(background.shape[0], y_offset + fg_height)
    x1_bg = max(0, x_offset)
    x2_bg = min(background.shape[1], x_offset + fg_width)

    if (y2_bg <= y1_bg) or (x2_bg <= x1_bg):
        return

    fg_y1_slice = 0 if y_offset >= 0 else -y_offset
    fg_y2_slice = fg_y1_slice + (y2_bg - y1_bg)
    
    fg_x1_slice = 0 if x_offset >= 0 else -x_offset
    fg_x2_slice = fg_x1_slice + (x2_bg - x1_bg)

    alpha_channel = foreground[fg_y1_slice:fg_y2_slice, fg_x1_slice:fg_x2_slice, 3] / 255.0
    alpha_factor = cv2.merge([alpha_channel, alpha_channel, alpha_channel])

    fg_colors = foreground[fg_y1_slice:fg_y2_slice, fg_x1_slice:fg_x2_slice, :3]

    background_roi = background[y1_bg:y2_bg, x1_bg:x2_bg]
    blended_roi = (background_roi * (1 - alpha_factor) + fg_colors * alpha_factor).astype(np.uint8)
    
    background[y1_bg:y2_bg, x1_bg:x2_bg] = blended_roi

# --- Car Class for Simulation ---
class Car:
    def __init__(self, x, y, direction, sprite_name):
        self.x = float(x)
        self.y = float(y)
        self.direction = direction # 'N', 'S', 'E', 'W'
        self.sprite_name = sprite_name
        self.speed = random.uniform(CAR_SPEED_MIN, CAR_SPEED_MAX)
        self.original_sprite = car_sprites[sprite_name]

        render_size = random.randint(CAR_RENDER_SIZE_MIN, CAR_RENDER_SIZE_MAX)
        aspect_ratio = self.original_sprite.shape[1] / self.original_sprite.shape[0]
        self.height = float(render_size)
        self.width = float(render_size * aspect_ratio)

        self.sprite = None
        self.is_stopped = False

        # Rotation angles for cars (assuming default sprite faces UP/North)
        self.rotation_angles = {
            'N': 0,    # North (Up)
            'S': 180,  # South (Down)
            'E': 270,  # East (Right)
            'W': 90    # West (Left)
        }
        # Cars will always face their initial direction
        self.current_angle = self.rotation_angles[self.direction]

    def update(self):
        if self.is_stopped:
            return

        # Cars only move straight
        if self.direction == 'N':
            self.y -= self.speed
        elif self.direction == 'S':
            self.y += self.speed
        elif self.direction == 'E':
            self.x += self.speed
        elif self.direction == 'W':
            self.x -= self.speed

    def is_offscreen(self):
        return (self.x < -self.width or self.x > CANVAS_WIDTH or
                self.y < -self.height or self.y > CANVAS_HEIGHT)

# --- Drawing Functions ---
def draw_road(frame):
    frame[:] = background_img[:]

    # You can add visible stop lines here if your background image doesn't have them
    center_x = CANVAS_WIDTH // 2
    center_y = CANVAS_HEIGHT // 2
    line_color = (0, 0, 255) # Red stop line
    line_thickness = 3

    # Stop line for NS traffic going South (coming from top, stopping before intersection)
    cv2.line(frame, (int(center_x - ROAD_WIDTH // 2), int(center_y - NS_STOP_LINE_OFFSET)),
                     (int(center_x + ROAD_WIDTH // 2), int(center_y - NS_STOP_LINE_OFFSET)), line_color, line_thickness)
    # Stop line for NS traffic going North (coming from bottom, stopping before intersection)
    cv2.line(frame, (int(center_x - ROAD_WIDTH // 2), int(center_y + NS_STOP_LINE_OFFSET)),
                     (int(center_x + ROAD_WIDTH // 2), int(center_y + NS_STOP_LINE_OFFSET)), line_color, line_thickness)

    # Stop line for EW traffic going East (coming from left, stopping before intersection)
    cv2.line(frame, (int(center_x - EW_STOP_LINE_OFFSET), int(center_y - ROAD_WIDTH // 2)),
                     (int(center_x - EW_STOP_LINE_OFFSET), int(center_y + ROAD_WIDTH // 2)), line_color, line_thickness)
    # Stop line for EW traffic going West (coming from right, stopping before intersection)
    cv2.line(frame, (int(center_x + EW_STOP_LINE_OFFSET), int(center_y - ROAD_WIDTH // 2)),
                     (int(center_x + EW_STOP_LINE_OFFSET), int(center_y + ROAD_WIDTH // 2)), line_color, line_thickness)


def draw_traffic_lights(frame):
    center_x = CANVAS_WIDTH // 2
    center_y = CANVAS_HEIGHT // 2
    light_radius = 12
    offset = ROAD_WIDTH // 2 + 15

    GREEN = (72, 187, 72)
    YELLOW = (75, 201, 236)
    RED = (68, 68, 239)

    ns_light_color = RED
    ew_light_color = RED

    if signal_state == 'GREEN':
        if current_signal == 'NS':
            ns_light_color = GREEN
        else:
            ew_light_color = GREEN
    elif signal_state == 'YELLOW':
        if current_signal == 'NS':
            ns_light_color = YELLOW
        else:
            ew_light_color = YELLOW

    # Draw traffic lights (simplified, can be improved with actual light positions)
    # Top-right light (NS direction)
    cv2.circle(frame, (int(center_x + offset), int(center_y - offset)), light_radius, ns_light_color, -1)
    cv2.circle(frame, (int(center_x + offset), int(center_y - offset)), light_radius, (50, 50, 50), 2)

    # Bottom-left light (NS direction)
    cv2.circle(frame, (int(center_x - offset), int(center_y + offset)), light_radius, ns_light_color, -1)
    cv2.circle(frame, (int(center_x - offset), int(center_y + offset)), light_radius, (50, 50, 50), 2)

    # Top-left light (EW direction)
    cv2.circle(frame, (int(center_x - offset), int(center_y - offset)), light_radius, ew_light_color, -1)
    cv2.circle(frame, (int(center_x - offset), int(center_y - offset)), light_radius, (50, 50, 50), 2)

    # Bottom-right light (EW direction)
    cv2.circle(frame, (int(center_x + offset), int(center_y + offset)), light_radius, ew_light_color, -1)
    cv2.circle(frame, (int(center_x + offset), int(center_y + offset)), light_radius, (50, 50, 50), 2)


def draw_cars(frame, cars):
    for car in cars:
        # Use the car's current_angle for dynamic rotation during turns
        angle = car.current_angle

        base_sprite = car.original_sprite
        (h, w) = base_sprite.shape[:2]
        (cX, cY) = (w // 2, h // 2)

        M = cv2.getRotationMatrix2D((cX, cY), angle, 1.0)
        rotated_sprite = cv2.warpAffine(base_sprite, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_CONSTANT, borderValue=(0,0,0,0))
        
        car.sprite = cv2.resize(rotated_sprite, (int(car.width), int(car.height)), interpolation=cv2.INTER_AREA)
        overlay_alpha_image(frame, car.sprite, car.x, car.y)

# --- Simulation Logic ---
def spawn_car():
    center_x = CANVAS_WIDTH // 2
    center_y = CANVAS_HEIGHT // 2

    available_sprites = list(car_sprites.keys())
    if not available_sprites:
        print("No car sprites loaded! Cannot spawn cars.")
        return

    random_sprite_name = random.choice(available_sprites)
    
    # Cars only go straight, so we place them in the correct lane
    road_choice = random.random()

    # Determine a slightly higher chance for NS traffic for testing the default
    # You can adjust these probabilities
    if road_choice < 0.5: # 60% chance for NS road
        if len(ns_cars) < MAX_CARS_PER_ROAD:
            direction_choice = random.random()
            if direction_choice < 0.5: # South-bound (from top, right lane for straight)
                spawn_x = center_x + LANE_WIDTH // 2 - CAR_RENDER_SIZE_MAX // 2
                ns_cars.append(Car(spawn_x, -CAR_RENDER_SIZE_MAX, 'S', random_sprite_name))
            else: # North-bound (from bottom, right lane for straight)
                spawn_x = center_x - LANE_WIDTH // 2 - CAR_RENDER_SIZE_MAX // 2
                ns_cars.append(Car(spawn_x, CANVAS_HEIGHT, 'N', random_sprite_name))
    else: # EW Road (40% chance)
        if len(ew_cars) < MAX_CARS_PER_ROAD:
            direction_choice = random.random()
            if direction_choice < 0.5: # East-bound (from left, right lane for straight)
                spawn_y = center_y + LANE_WIDTH // 2 - CAR_RENDER_SIZE_MAX // 2
                ew_cars.append(Car(-CAR_RENDER_SIZE_MAX, spawn_y, 'E', random_sprite_name))
            else: # West-bound (from right, right lane for straight)
                spawn_y = center_y - LANE_WIDTH // 2 - CAR_RENDER_SIZE_MAX // 2
                ew_cars.append(Car(CANVAS_WIDTH, spawn_y, 'W', random_sprite_name))

def update_cars():
    global ns_cars, ew_cars
    center_x = CANVAS_WIDTH // 2
    center_y = CANVAS_HEIGHT // 2

    # Stop distances for NS cars
    # South-bound cars stop when their front reaches this Y coordinate
    stop_y_southbound = center_y - NS_STOP_LINE_OFFSET
    # North-bound cars stop when their front reaches this Y coordinate
    stop_y_northbound = center_y + NS_STOP_LINE_OFFSET

    # Stop distances for EW cars
    # East-bound cars stop when their front reaches this X coordinate
    stop_x_eastbound = center_x - EW_STOP_LINE_OFFSET
    # West-bound cars stop when their front reaches this X coordinate
    stop_x_westbound = center_x + EW_STOP_LINE_OFFSET

    # Update NS cars
    for i, car in enumerate(ns_cars):
        car.is_stopped = False # Reset stop status

        # Logic for stopping at red light (adjusted for precise stopping)
        if signal_state != 'GREEN' or current_signal != 'NS':
            if car.direction == 'S': # South-bound car (moving down)
                # If car's front is about to cross the stop line
                if car.y + car.height > stop_y_southbound - car.speed and car.y < stop_y_southbound:
                    car.y = stop_y_southbound - car.height # Position exactly at the stop line
                    car.is_stopped = True
            elif car.direction == 'N': # North-bound car (moving up)
                # If car's front is about to cross the stop line
                if car.y < stop_y_northbound + car.speed and car.y + car.height > stop_y_northbound:
                    car.y = stop_y_northbound # Position exactly at the stop line
                    car.is_stopped = True
        
        # Check for car-to-car collisions (queuing) for NS cars
        if not car.is_stopped: # If not stopped by a light, check for cars ahead
            for j, other_car in enumerate(ns_cars):
                if i != j and car.direction == other_car.direction: # Check cars in the same direction
                    # Collision detection (simple bounding box overlap for queuing)
                    if car.direction == 'S': # South-bound
                        # If 'car' is behind 'other_car' and too close
                        if car.y + car.height < other_car.y + other_car.height and \
                           car.y + car.height + car.speed + 5 > other_car.y: # +5 for small buffer
                            if other_car.is_stopped or (car.y + car.height > other_car.y - 10): # If other car is stopped or very close
                                car.y = other_car.y - car.height - 5 # Stop behind it
                                car.is_stopped = True
                                break
                    elif car.direction == 'N': # North-bound
                        # If 'car' is behind 'other_car' and too close
                        if car.y > other_car.y and \
                           car.y - car.speed - 5 < other_car.y + other_car.height: # -5 for small buffer
                            if other_car.is_stopped or (car.y < other_car.y + other_car.height + 10): # If other car is stopped or very close
                                car.y = other_car.y + other_car.height + 5 # Stop behind it
                                car.is_stopped = True
                                break
        car.update()


    # Update EW cars (similar logic)
    for i, car in enumerate(ew_cars):
        car.is_stopped = False

        # Logic for stopping at red light (adjusted for precise stopping)
        if signal_state != 'GREEN' or current_signal != 'EW':
            if car.direction == 'E': # East-bound car (moving right)
                if car.x + car.width > stop_x_eastbound - car.speed and car.x < stop_x_eastbound:
                    car.x = stop_x_eastbound - car.width
                    car.is_stopped = True
            elif car.direction == 'W': # West-bound car (moving left)
                if car.x < stop_x_westbound + car.speed and car.x + car.width > stop_x_westbound:
                    car.x = stop_x_westbound
                    car.is_stopped = True

        # Check for car-to-car collisions (queuing) for EW cars
        if not car.is_stopped:
            for j, other_car in enumerate(ew_cars):
                if i != j and car.direction == other_car.direction:
                    if car.direction == 'E': # East-bound
                        if car.x + car.width < other_car.x + other_car.width and \
                           car.x + car.width + car.speed + 5 > other_car.x:
                            if other_car.is_stopped or (car.x + car.width > other_car.x - 10):
                                car.x = other_car.x - car.width - 5
                                car.is_stopped = True
                                break
                    elif car.direction == 'W': # West-bound
                        if car.x > other_car.x and \
                           car.x - car.speed - 5 < other_car.x + other_car.width:
                            if other_car.is_stopped or (car.x < other_car.x + other_car.width + 10):
                                car.x = other_car.x + other_car.width + 5
                                car.is_stopped = True
                                break
        car.update()

    ns_cars = [car for car in ns_cars if not car.is_offscreen()]
    ew_cars = [car for car in ew_cars if not car.is_offscreen()]


# --- Traffic Analysis (Simulated OpenCV Detection) ---
def get_traffic_density(cars, road_direction):
    count = 0
    # Define the actual detection zones based on the road layout
    if road_direction == 'NS':
        # We'll consider cars within a slightly wider area around the stop lines for 'density'
        for car in cars:
            if (car.x + car.width > CANVAS_WIDTH // 2 - ROAD_WIDTH // 2 and
                car.x < CANVAS_WIDTH // 2 + ROAD_WIDTH // 2 and
                car.y + car.height > CANVAS_HEIGHT // 2 - NS_STOP_LINE_OFFSET - 50 and
                car.y < CANVAS_HEIGHT // 2 + NS_STOP_LINE_OFFSET + 50): # Broadened detection zone
                count += 1
    elif road_direction == 'EW':
        # Check if car's bounding box overlaps with EW detection zone
        for car in cars:
            if (car.y + car.height > CANVAS_HEIGHT // 2 - ROAD_WIDTH // 2 and
                car.y < CANVAS_HEIGHT // 2 + ROAD_WIDTH // 2 and
                car.x + car.width > CANVAS_WIDTH // 2 - EW_STOP_LINE_OFFSET - 50 and
                car.x < CANVAS_WIDTH // 2 + EW_STOP_LINE_OFFSET + 50): # Broadened detection zone
                count += 1
    return count

def get_queue_length(cars, road_direction):
    queue_count = 0
    center_x = CANVAS_WIDTH // 2
    center_y = CANVAS_HEIGHT // 2

    # These stop lines are where cars queue.
    stop_y_southbound = center_y - NS_STOP_LINE_OFFSET
    stop_y_northbound = center_y + NS_STOP_LINE_OFFSET
    stop_x_eastbound = center_x - EW_STOP_LINE_OFFSET
    stop_x_westbound = center_x + EW_STOP_LINE_OFFSET

    if road_direction == 'NS':
        for car in cars:
            if car.is_stopped:
                # Check if the car is stopped at its respective stop line
                if (car.direction == 'S' and abs((car.y + car.height) - stop_y_southbound) < car.speed + 5) or \
                   (car.direction == 'N' and abs(car.y - stop_y_northbound) < car.speed + 5):
                    queue_count += 1
    elif road_direction == 'EW':
        for car in cars:
            if car.is_stopped:
                if (car.direction == 'E' and abs((car.x + car.width) - stop_x_eastbound) < car.speed + 5) or \
                   (car.direction == 'W' and abs(car.x - stop_x_westbound) < car.speed + 5):
                    queue_count += 1
    return queue_count

# --- Traffic Signal Control Logic ---
def update_signal():
    global current_signal, signal_state, signal_timer_start_time

    elapsed_time = time.time() - signal_timer_start_time

    ns_queue = get_queue_length(ns_cars, 'NS')
    ew_queue = get_queue_length(ew_cars, 'EW')

    # Define thresholds for "significant" queue
    MIN_QUEUE_TO_SWITCH = 2 # Number of cars that makes a queue 'significant' for switching
    NO_QUEUE_THRESHOLD = 0 # If current road has 0 cars, it's a good candidate to switch

    if signal_state == 'GREEN':
        should_switch = False

        if current_signal == 'NS':
            # Priority switch if NS has no cars and EW has traffic
            if ns_queue <= NO_QUEUE_THRESHOLD and ew_queue > NO_QUEUE_THRESHOLD and elapsed_time >= MIN_GREEN_TIME_SEC:
                should_switch = True
            # Smart switch: if NS queue is low and EW queue is significant
            elif elapsed_time >= MIN_GREEN_TIME_SEC and ns_queue < ew_queue and ew_queue >= MIN_QUEUE_TO_SWITCH:
                should_switch = True
            # Max green time reached
            elif elapsed_time >= MAX_GREEN_TIME_SEC:
                should_switch = True
                
        else: # current_signal == 'EW'
            # Priority switch if EW has no cars and NS has traffic
            if ew_queue <= NO_QUEUE_THRESHOLD and ns_queue > NO_QUEUE_THRESHOLD and elapsed_time >= MIN_GREEN_TIME_SEC:
                should_switch = True
            # Smart switch: if EW queue is low and NS queue is significant
            elif elapsed_time >= MIN_GREEN_TIME_SEC and ew_queue < ns_queue and ns_queue >= MIN_QUEUE_TO_SWITCH:
                should_switch = True
            # Max green time reached
            elif elapsed_time >= MAX_GREEN_TIME_SEC:
                should_switch = True

        if should_switch:
            signal_state = 'YELLOW'
            signal_timer_start_time = time.time()

    elif signal_state == 'YELLOW':
        if elapsed_time >= YELLOW_TIME_SEC:
            signal_state = 'RED'
            signal_timer_start_time = time.time()

    elif signal_state == 'RED':
        if elapsed_time >= RED_TRANSITION_TIME_SEC:
            # Decide next green based on which queue is longer
            if ns_queue > ew_queue:
                current_signal = 'NS'
            elif ew_queue > ns_queue:
                current_signal = 'EW'
            else:
                # Default to NS if queues are equal or both empty
                current_signal = 'NS' 

            signal_state = 'GREEN'
            signal_timer_start_time = time.time()

    return ns_queue, ew_queue

# --- Image Loading Function ---
def load_assets():
    global background_img, car_sprites

    try:
        bg_img_raw = cv2.imread(BACKGROUND_IMAGE_PATH)
        if bg_img_raw is None:
            raise FileNotFoundError(f"Background image not found at: {BACKGROUND_IMAGE_PATH}")
        background_img = cv2.resize(bg_img_raw, (CANVAS_WIDTH, CANVAS_HEIGHT), interpolation=cv2.INTER_AREA)
    except Exception as e:
        print(f"Error loading background image: {e}")
        print("Using a solid gray background instead.")
        background_img = np.zeros((CANVAS_HEIGHT, CANVAS_WIDTH, 3), dtype=np.uint8)
        background_img[:] = (100, 100, 100) # Fallback to gray

    if not os.path.exists(CAR_SPRITE_DIR):
        print(f"Car sprites directory '{CAR_SPRITE_DIR}' not found. Cars will not be drawn.")
        return

    for filename in os.listdir(CAR_SPRITE_DIR):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            filepath = os.path.join(CAR_SPRITE_DIR, filename)
            sprite = cv2.imread(filepath, cv2.IMREAD_UNCHANGED)
            if sprite is not None:
                if sprite.shape[2] == 4: # Has alpha channel
                    car_sprites[os.path.splitext(filename)[0]] = sprite
                else: # No alpha channel, convert to BGRA
                    print(f"Warning: Sprite '{filename}' does not have an alpha channel. Converting.")
                    car_sprites[os.path.splitext(filename)[0]] = cv2.cvtColor(sprite, cv2.COLOR_BGR2BGRA)
            else:
                print(f"Warning: Could not load sprite: {filename}")

# --- Main Simulation Loop ---
def main():
    global frameCount

    load_assets()

    frame = np.zeros((CANVAS_HEIGHT, CANVAS_WIDTH, 3), dtype=np.uint8)

    # Background subtractor (for simulated detection, not directly used for signal logic)
    fgbg = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=16, detectShadows=True)

    print("Starting Traffic Simulation & Analysis (Python with OpenCV)")
    print("Press 'q' to quit.")

    frameCount = 0

    while True:
        draw_road(frame) # Draw background and stop lines
        draw_cars(frame, ns_cars)
        draw_cars(frame, ew_cars)
        draw_traffic_lights(frame)

        update_cars() # Update car positions and stop status
        frameCount += 1
        if frameCount % SPAWN_INTERVAL_FRAMES == 0:
            spawn_car()

        # --- OpenCV Detection (for visual feedback, not direct control) ---
        detection_frame = frame.copy()
        fgmask = fgbg.apply(detection_frame)

        kernel = np.ones((5, 5), np.uint8)
        fgmask = cv2.erode(fgmask, kernel, iterations=1)
        fgmask = cv2.dilate(fgmask, kernel, iterations=2)

        contours, _ = cv2.findContours(fgmask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Draw detection zones (can be made invisible in final version)
        cv2.rectangle(frame, (int(CANVAS_WIDTH // 2 - ROAD_WIDTH // 2), int(CANVAS_HEIGHT // 2 - NS_STOP_LINE_OFFSET - 140)),
                      (int(CANVAS_WIDTH // 2 + ROAD_WIDTH // 2), int(CANVAS_HEIGHT // 2 + NS_STOP_LINE_OFFSET + 140)), (0, 255, 255), 2)
        cv2.rectangle(frame, (int(CANVAS_WIDTH // 2 - EW_STOP_LINE_OFFSET - 200), int(CANVAS_HEIGHT // 2 - ROAD_WIDTH // 2)),
                      (int(CANVAS_WIDTH // 2 + EW_STOP_LINE_OFFSET + 200), int(CANVAS_HEIGHT // 2 + ROAD_WIDTH // 2)), (255, 0, 255), 2)

        detected_ns_count = 0
        detected_ew_count = 0

        for contour in contours:
            area = cv2.contourArea(contour)
            if area < CAR_RENDER_SIZE_MIN * CAR_RENDER_SIZE_MIN * 0.5: # Filter out small noise
                continue

            x, y, w, h = cv2.boundingRect(contour)

            # Check if contour is within NS detection zone
            if (x + w > CANVAS_WIDTH // 2 - ROAD_WIDTH // 2 and x < CANVAS_WIDTH // 2 + ROAD_WIDTH // 2 and
                y + h > CANVAS_HEIGHT // 2 - NS_STOP_LINE_OFFSET - 120 and y < CANVAS_HEIGHT // 2 + NS_STOP_LINE_OFFSET + 120):
                detected_ns_count += 1
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2) # Green for NS detection

            # Check if contour is within EW detection zone
            if (y + h > CANVAS_HEIGHT // 2 - ROAD_WIDTH // 2 and y < CANVAS_HEIGHT // 2 + ROAD_WIDTH // 2 and
                x + w > CANVAS_WIDTH // 2 - EW_STOP_LINE_OFFSET - 120 and x < CANVAS_WIDTH // 2 + EW_STOP_LINE_OFFSET + 120):
                detected_ew_count += 1
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2) # Blue for EW detection


        # Update signal logic based on *queue lengths*
        ns_queue_length, ew_queue_length = update_signal()

        # Display information on screen
        cv2.putText(frame, f"NS Queue: {ns_queue_length}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, f"EW Queue: {ew_queue_length}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, f"NS Detected: {detected_ns_count}", (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, f"EW Detected: {detected_ew_count}", (10, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

        signal_text = f"Signal: {current_signal} {signal_state}"
        signal_color = (255, 255, 255)
        if signal_state == 'GREEN':
            signal_color = (0, 255, 0) # Green light for active signal
        elif signal_state == 'YELLOW':
            signal_color = (0, 255, 255) # Yellow light
        elif signal_state == 'RED':
            signal_color = (0, 0, 255) # Red light

        cv2.putText(frame, signal_text, (CANVAS_WIDTH - 250, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, signal_color, 2)

        cv2.imshow('Traffic Simulation & Analysis (OpenCV)', frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

    cv2.destroyAllWindows()
    print("Simulation ended.")

if __name__ == "__main__":
    main()