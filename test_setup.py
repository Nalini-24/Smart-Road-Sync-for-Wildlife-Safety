import tensorflow as tf
import keras
import cv2
import numpy as np

print("✅ TensorFlow version:", tf.__version__)
print("✅ Keras version:", keras.__version__)
print("✅ OpenCV version:", cv2.__version__)
print("✅ NumPy version:", np.__version__)

# Simple TensorFlow test
hello = tf.constant("Hello TensorFlow!")
print("TensorFlow says:", hello.numpy().decode("utf-8"))
