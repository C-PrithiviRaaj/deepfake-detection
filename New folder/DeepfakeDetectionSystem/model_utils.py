import numpy as np
from PIL import Image
import os

try:
    import tensorflow as tf
    # Suppress TF warnings
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
    TF_AVAILABLE = True
except ImportError:
    print("[WARNING] TensorFlow not found. Running in dummy prediction mode.")
    TF_AVAILABLE = False

MODEL_PATH = 'model/deepfake_model.h5'
IMG_SIZE = (128, 128)

# Global model variable
model = None

def load_model():
    global model
    if model is None:
        if TF_AVAILABLE and os.path.exists(MODEL_PATH):
            try:
                model = tf.keras.models.load_model(MODEL_PATH)
                print("[SUCCESS] Model loaded successfully.")
            except Exception as e:
                print(f"[ERROR] Error loading model: {e}")
        else:
            print("[WARNING] Model not found or TensorFlow unavailable. Returning a dummy prediction for testing.")

def detect_image(image_path):
    """
    Loads an image, preprocesses it, and predicts if it's REAL or FAKE.
    Returns: (label, confidence_percentage)
    """
    load_model()
    
    try:
        # Load and resize image
        img = Image.open(image_path).convert('RGB')
        img = img.resize(IMG_SIZE)
        
        # Convert to numpy array and normalize
        img_array = np.array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0) # Add batch dimension
        
        if model is not None:
            # Predict
            prediction = model.predict(img_array)[0][0]
            
            # Since generator uses alphanumeric sorting, class indices are typically:
            # fake = 0, real = 1
            # If prediction > 0.5, it's real.
            if prediction > 0.5:
                label = "REAL"
                confidence = prediction * 100
            else:
                label = "FAKE"
                confidence = (1 - prediction) * 100
                
            return label, round(confidence, 2)
        else:
            # Dummy fallback if no model exists yet
            import random
            is_real = random.choice([True, False])
            confidence = round(random.uniform(50.0, 99.9), 2)
            return "REAL" if is_real else "FAKE", confidence
            
    except Exception as e:
        print(f"Error predicting image: {e}")
        return "ERROR", 0.0
