import serial
import time

# Update COM port if needed
arduino = serial.Serial("COM6", 9600, timeout=1)
time.sleep(2)  # Allow Arduino to reset

while True:
    print("Sending ANIMAL...")
    arduino.write(b"ANIMAL\n")
    time.sleep(2)

    print("Sending NONE...")
    arduino.write(b"NONE\n")
    time.sleep(2)
