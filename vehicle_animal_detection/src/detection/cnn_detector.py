import os
import cv2
import numpy as np
import tensorflow as tf
import yaml

class CNNDetector:
    def __init__(self, config):
        self.config = config

        # Load model
        model_path = os.path.join("models", "train_history_3_blocks_32_64_128_1_dense_drop_batch.h5")
        self.model = tf.keras.models.load_model(model_path)

        # Load class labels from config.yaml
        with open(config, "r") as f:
            cfg = yaml.safe_load(f)
        self.class_labels = cfg.get("class_labels", ["animal", "vehicle", "unknown"])

        print(f"[INFO] CNNDetector initialized with {len(self.class_labels)} classes.")

    def predict(self, frame):
        """Run prediction on a video frame."""
        img = cv2.resize(frame, (64, 64))   # adjust size to what your model expects
        img = img / 255.0
        img = np.expand_dims(img, axis=0)

        preds = self.model.predict(img)
        class_id = np.argmax(preds)
        label = self.class_labels[class_id]
        confidence = float(np.max(preds))

        return label, confidence
