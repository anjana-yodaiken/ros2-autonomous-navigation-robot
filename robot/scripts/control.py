import serial
import time
import threading

ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
time.sleep(2)

# Background thread — reads everything coming from Arduino
def read_loop():
    while True:
        line = ser.readline().decode().strip()
        if line.startswith("ENC"):
            parts = line.split()
            left_ticks = int(parts[1])
            right_ticks = int(parts[2])
            print(f"ENC → left: {left_ticks}  right: {right_ticks}")
        elif line:
            print(f"Arduino: {line}")

thread = threading.Thread(target=read_loop, daemon=True)
thread.start()

# Main loop — send commands
def send_vel(left, right):
    cmd = f"VEL {left:.2f} {right:.2f}\n"
    ser.write(cmd.encode())

send_vel(0.5, 0.5)
time.sleep(2)
send_vel(0.0, 0.0)

# Keep script alive so reader thread keeps running
while True:
    time.sleep(1)