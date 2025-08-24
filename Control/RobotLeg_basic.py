
### INITIAL DOC
## Power dist (DC, shared GND)
# - 35kgcm is 4.8~8.4V; 60kgcm is 6~8.4V
# - PCA9685 logic is 3.3V, power is max 5V -> Too weak for Servos
# - PCA9685 to Servo only for PWM, 8V Servo power line seperately (buck converter?)
# - MAX Current draw in theory: 
#
## Channel desc
#- (35kgcm) [0-2]   Hip roll/pitch/jaw 
#- (60kgcm) [3]     Knee
#- (35kgcm) [4]     Foot
#
## Brief Building instructions
#- Refer to Legolas Biped GitHub for basic part CAD setup (STL/Solidworks)
#- Printing was done in PLA with more wall layers/infill (probably better: PETG/ABS)
#- Set servos to 90° (ideally real life correction) before assembly
#- Part assembly with direct screwing, locking nuts (M2, M3, M4)
###

### SOFTWARE
#- UI with sliders for each DOF and Sweep switch (max current draw est)
#- There seems to be a bug where servo [2] could not stop sweeping

import tkinter as tk
from tkinter import messagebox
from adafruit_servokit import ServoKit
import board
import busio
import threading
import time

# Initialize I2C and ServoKit
i2c_bus = busio.I2C(board.SCL, board.SDA)
kit = ServoKit(channels=16, i2c=i2c_bus)

#For Button control
def set_all_servos(angle):
    for i in range(5):
        # Skip if sweep is active for a servo
        _, var = sweep_checkboxes[i]
        if not var.get():
            kit.servo[i].angle = angle
            update_ui(i, angle)

# Function to update servo angle from slider
def update_servo_angle(servo_index, angle):
    angle = int(angle)
    kit.servo[servo_index].angle = angle
    update_ui(servo_index, angle)

# Function to handle editable angle field input
def set_angle_from_entry(servo_index):
    try:
        angle = int(entry_fields[servo_index].get())
        if 0 <= angle <= 180:
            kit.servo[servo_index].angle = angle
            update_ui(servo_index, angle)
        else:
            messagebox.showwarning("Invalid Angle", "Please enter an angle between 0 and 180.")
    except ValueError:
        messagebox.showwarning("Invalid Input", "Please enter a valid integer.")


# Function to handle the sweep checkbox
def toggle_sweep(servo_index):
    _, var = sweep_checkboxes[servo_index]
    is_sweeping = var.get()

    if is_sweeping:
        # Disable UI while sweeping
        entry_fields[servo_index].config(state=tk.DISABLED)
        sliders[servo_index].config(state=tk.DISABLED)

        # Start a thread that loops the sweep
        def sweep_loop():
            while var.get():
                for angle in range(0, 181, 2):
                    kit.servo[servo_index].angle = angle
                    update_ui(servo_index, angle)
                    time.sleep(0.02)
                    if not var.get():
                        break
                for angle in range(180, -1, -2):
                    kit.servo[servo_index].angle = angle
                    update_ui(servo_index, angle)
                    time.sleep(0.02)
                    if not var.get():
                        break
            # Re-enable UI when done
            update_ui(servo_index)

        t = threading.Thread(target=sweep_loop, daemon=True)
        t.start()
        sweep_threads[servo_index] = t
    else:
        # Sweep thread will stop and update_ui will re-enable inputs
        pass

def update_ui(servo_index, angle=None):
    # If no angle provided, use last known slider value
    if angle is None:
        angle = kit.servo[servo_index].angle or 0

    angle = int(angle)

    # Update angle display in entry field
    entry_fields[servo_index].config(state=tk.NORMAL)
    entry_fields[servo_index].delete(0, tk.END)
    entry_fields[servo_index].insert(0, str(angle))

    # Update slider position
    sliders[servo_index].config(state=tk.NORMAL)
    sliders[servo_index].set(angle)

    # Disable entry + slider if sweep is active
    _, var = sweep_checkboxes[servo_index]
    if var.get():
        entry_fields[servo_index].config(state=tk.DISABLED)
        sliders[servo_index].config(state=tk.DISABLED)

### UI

# Create main Tkinter window
root = tk.Tk()
root.title("3D-Druck Dulli Leg Controller")
root.geometry("500x600")
root.resizable(False, False)

# Add global control buttons
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

reset_btn = tk.Button(button_frame, text="Reset (90°)", command=lambda: set_all_servos(90), width=12)
reset_btn.grid(row=0, column=0, padx=5)

min_btn = tk.Button(button_frame, text="Min (0°)", command=lambda: set_all_servos(0), width=12)
min_btn.grid(row=0, column=1, padx=5)

max_btn = tk.Button(button_frame, text="Max (180°)", command=lambda: set_all_servos(180), width=12)
max_btn.grid(row=0, column=2, padx=5)


# Label for the headline
#headline = tk.Label(root, text="3D-Druck Dulli Leg Controller", font=("Arial", 18), anchor="w")
#headline.pack(fill=tk.X, padx=10, pady=10)

servo_names = [
    "Hip roll",
    "Hip pitch",
    "Hip yaw",
    "Knee",
    "Foot"
]
angle_labels = []  # Labels to display the angle
entry_fields = []  # Entry fields for angle input
sweep_checkboxes = []  # Checkbox for servo sweep
sweep_threads = [None] * 5  # List to keep track of threads for sweep mechanism
sliders = []

# Create UI for each servo
for i in range(5):
    frame = tk.Frame(root)
    frame.pack(fill=tk.X, padx=10, pady=5)

    # Line 1: Name, Current Angle, and Sweep checkbox
    name_label = tk.Label(frame, text=servo_names[i], font=("Arial", 12))
    name_label.grid(row=0, column=0, padx=5, pady=5)

    # Entry field for editable angle input
    entry_field = tk.Entry(frame, width=5)
    entry_field.insert(0, "90")  # Default angle is 90 degrees
    entry_field.grid(row=0, column=2, padx=5, pady=5)
    entry_fields.append(entry_field)

    # Sweep checkbox
    sweep_var = tk.BooleanVar()
    sweep_checkbox = tk.Checkbutton(frame, text="Sweep", variable=sweep_var, command=lambda i=i: toggle_sweep(i))
    sweep_checkbox.grid(row=0, column=3, padx=5, pady=5)
    sweep_checkboxes.append((sweep_checkbox, sweep_var))  # store both


    # Line 2: Slider for adjusting servo angle
    slider = tk.Scale(frame, from_=0, to=180, orient=tk.HORIZONTAL, length=200, command=lambda val, i=i: update_servo_angle(i, val))
    slider.set(90)  # Default slider value is 90 degrees
    slider.grid(row=1, column=0, columnspan=4, padx=5, pady=5)
    sliders.append(slider)


    # Bind the entry field to update angle when edited
    entry_field.bind("<Return>", lambda event, i=i: set_angle_from_entry(i))

# Start the Tkinter event loop
print("Starting PCA9685 Servo Control UI...")
root.mainloop()