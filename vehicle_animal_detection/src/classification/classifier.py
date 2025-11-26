import yaml
import cv2
import numpy as np

class Classifier:
    def __init__(self, config_path):
        # Load configuration but skip CNN model
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        print("[INFO] CNNClassifier bypassed. Using YOLO detection only.")
        self.confidence_threshold = self.config['models']['classifier'].get('confidence_threshold', 0.5)

    def preprocess_image(self, image):
        # Dummy method: just return the input frame
        return image

    def classify(self, image):
        # Dummy method: YOLO handles detection, return None
        return None
