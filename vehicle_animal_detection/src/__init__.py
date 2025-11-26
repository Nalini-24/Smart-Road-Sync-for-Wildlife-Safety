import serial
import time
from .classification import Classifier
from .gui import MainWindow

class ArduinoHandler:
    def __init__(self, port='COM3', baudrate=9600):
        """Initialize Arduino connection."""
        try:
            self.arduino = serial.Serial(port=port, baudrate=baudrate, timeout=1)
            time.sleep(2)  # wait for Arduino to initialize
            print(f"[INFO] Arduino connected successfully on {port}.")
        except Exception as e:
            print(f"[WARNING] Could not connect to Arduino: {e}")
            self.arduino = None

    def send(self, message: str):
        """Send a message to Arduino if connected."""
        if self.arduino:
            try:
                self.arduino.write((message + '\n').encode('utf-8'))
                print(f"[INFO] Sent to Arduino: {message}")
            except Exception as e:
                print(f"[ERROR] Failed to send message: {e}")
        else:
            print("[WARNING] Arduino not connected. Message not sent.")
