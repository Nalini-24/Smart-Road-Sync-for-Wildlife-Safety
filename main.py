import sys
import os

# -----------------------------
# Add src folder to sys.path
# -----------------------------
project_root = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(project_root, "vehicle_animal_detection", "src")
if src_path not in sys.path:
    sys.path.append(src_path)

# -----------------------------
# Import PyQt and your GUI
# -----------------------------
from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow

# -----------------------------
# Import TensorFlow / Keras if needed
# -----------------------------
import tensorflow as tf
print("TensorFlow version:", tf.__version__)

# -----------------------------
# Main function
# -----------------------------
def main():
    print("Starting Animal Recognition App...")
    app = QApplication(sys.argv)
    
    # Correct path to config.yaml
    config_path = os.path.join(project_root, "vehicle_animal_detection", "config", "config.yaml")
    
    # Instantiate the GUI with config
    window = MainWindow(config_path)
    window.show()
    
    sys.exit(app.exec_())

# -----------------------------
if __name__ == "__main__":
    main()






