import cv2
import RPi.GPIO as GPIO
import time

# Set up GPIO mode and pins
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT)
GPIO.setup(18, GPIO.OUT)
GPIO.setup(22, GPIO.OUT)
GPIO.setup(23, GPIO.OUT)
GPIO.setup(24, GPIO.OUT)
GPIO.setup(25, GPIO.OUT)

# Initialize PWM for motor speed control
pwm_motor1 = GPIO.PWM(24, 50)  # ENA - Motor 1 speed control
pwm_motor2 = GPIO.PWM(25, 50)  # ENB - Motor 2 speed control
pwm_motor1.start(0)  # Start with 0% duty cycle
pwm_motor2.start(0)

# Define motor control functions
def stop():
    GPIO.output(17, GPIO.LOW)
    GPIO.output(18, GPIO.LOW)
    GPIO.output(22, GPIO.LOW)
    GPIO.output(23, GPIO.LOW)

def move_forward(speed=50):
    pwm_motor1.ChangeDutyCycle(min(speed, 50))  # Limit speed to maximum of 50
    pwm_motor2.ChangeDutyCycle(min(speed, 50))
    GPIO.output(17, GPIO.HIGH)
    GPIO.output(18, GPIO.LOW)
    GPIO.output(22, GPIO.HIGH)
    GPIO.output(23, GPIO.LOW)

def turn_left(speed=50):
    pwm_motor1.ChangeDutyCycle(speed)
    pwm_motor2.ChangeDutyCycle(speed)
    GPIO.output(17, GPIO.LOW)
    GPIO.output(18, GPIO.HIGH)
    GPIO.output(22, GPIO.HIGH)
    GPIO.output(23, GPIO.LOW)

def turn_right(speed=50):
    pwm_motor1.ChangeDutyCycle(speed)
    pwm_motor2.ChangeDutyCycle(speed)
    GPIO.output(17, GPIO.HIGH)
    GPIO.output(18, GPIO.LOW)
    GPIO.output(22, GPIO.LOW)
    GPIO.output(23, GPIO.HIGH)

# Load pre-trained Haar Cascade classifier for pedestrian detection
pedestrian_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Initialize video capture from the Pi camera (assuming it's connected as '/dev/video0')
cap = cv2.VideoCapture(0)

# Define left and right lines for turning with increased space
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
space_between_lines = 30  # Adjust as needed
line_left = frame_width // 3 - space_between_lines
line_right = frame_width * 2 // 3 + space_between_lines

# PID parameters
Kp = 0.1  # Proportional control gain

# Main loop

try:
    last_detection_position = None  # Variable to store the last detected person's position
    
    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()
        
        if not ret:
            break
    
        # Convert frame to grayscale for pedestrian detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
        # Detect pedestrians in the frame
        pedestrians = pedestrian_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    
        # Draw left and right lines
        cv2.line(frame, (line_left, 0), (line_left, frame.shape[0]), (0, 255, 0), 2)
        cv2.line(frame, (line_right, 0), (line_right, frame.shape[0]), (0, 255, 0), 2)
        
        person_detected = False
        
        # Process detected pedestrians
        for (x, y, w, h) in pedestrians:
            person_detected = True
            # Draw a rectangle around the detected face
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
    
            # Calculate the center of the pedestrian bounding box
            pedestrian_center_x = x + w // 2
    
            # Move robot based on pedestrian position
            if line_left < pedestrian_center_x < line_right:
                # Move forward with dynamic speed adjustment based on distance
                speed = max(25, min(50, int(50 - (w / frame_width) * 50)))  # Adjust speed based on distance
                print("Move forward with speed:", speed)
                move_forward(speed)
                last_detection_position = 'forward'
            else:
                # Adjust orientation using proportional control
                error = frame_width // 2 - pedestrian_center_x
                turn_rate = Kp * error
                if turn_rate > 0:
                    print("Turn right")
                    turn_right(int(turn_rate))
                    last_detection_position = 'right'
                else:
                    print("Turn left")
                    turn_left(int(-turn_rate))
                    last_detection_position = 'left'
                
        # If no person detected
        if not person_detected:
            print("No person detected")
            #stop()
            turn_left()
            time.sleep(0.3)
            
            

            stop()
            # Turn in the direction where the last person was detected
        """if last_detection_position == 'forward':
            move_forward(25)  # Move forward with maximum speed
        elif last_detection_position == 'left':
            print("Turning left to find person")
            turn_left()
            time.sleep(0.5)  # Adjust as needed
            move_forward(25)  # Move forward with maximum speed after turning left
        elif last_detection_position == 'right':
            print("Turning right to find person")
            turn_right()
            time.sleep(0.5)  # Adjust as needed
            move_forward(25)  # Move forward with maximum speed after turning right
        """
        # Display the resulting frame
        cv2.imshow('Frame', frame)
    
        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
finally:
    # Release the capture
    cap.release()
    cv2.destroyAllWindows()
    
    # Stop motors and cleanup GPIO pins
    stop()
    pwm_motor1.stop()
    GPIO.cleanup()
        