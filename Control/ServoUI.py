import tkinter as tk
from adafruit_servokit import ServoKit
import board
import busio

# Initialize I2C and ServoKit
i2c_bus = busio.I2C(board.SCL, board.SDA)
kit = ServoKit(channels=16, i2c=i2c_bus)

# Function to update servo angle from slider
def update_servo(angle):
    angle = int(float(angle))  # Tkinter passes string values
    kit.servo[0].angle = angle
    angle_label.config(text=f"Angle: {angle}°")

# Create main Tkinter window
root = tk.Tk()
root.title("Servo Angle Controller")

# Window size and layout
root.geometry("300x150")
root.resizable(False, False)

# Angle label
angle_label = tk.Label(root, text="Angle: 90°", font=("Arial", 14))
angle_label.pack(pady=10)

# Slider widget (Scale)
angle_slider = tk.Scale(
    root,
    from_=0,
    to=180,
    orient=tk.HORIZONTAL,
    length=250,
    command=update_servo
)
angle_slider.set(90)  # Start at 90 degrees
angle_slider.pack(pady=5)

# Start the Tkinter event loop
print("Starting servo angle slider UI...")
root.mainloop()
