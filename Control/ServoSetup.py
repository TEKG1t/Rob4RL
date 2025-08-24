##
#- Initializes the servo (I2C with PCA9685)
#- Waits for user input from the terminal
#- Validates and caps the angle between 0 and 180
#- Moves the servo to the input angle
#- Waits briefly before prompting for the next input
##    

from adafruit_servokit import ServoKit
import board
import busio
import time

# Initialize I2C bus and ServoKit
i2c_bus = busio.I2C(board.SCL, board.SDA)
kit = ServoKit(channels=16, i2c=i2c_bus)

print("ServoKit initialized. Ready for angle input (0–180).")

while True:
    try:
        user_input = input("Enter angle (0–180) or 'q' to quit: ").strip()
        
        if user_input.lower() == 'q':
            print("Exiting.")
            break
        
        angle = int(user_input)

        # Cap the angle between 0 and 180
        angle = max(0, min(180, angle))
        
        # Move the servo (on channel 0)
        kit.servo[0].angle = angle
        print(f"Moved servo to {angle} degrees.")

        time.sleep(0.5)  # Short delay before next input

    except ValueError:
        print("Invalid input. Please enter a number between 0 and 180, or 'q' to quit.")

            