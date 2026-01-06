import base64
import cv2
import numpy as np
import face_recognition
from io import BytesIO
from PIL import Image

def generate_embedding(image_base64: str):
    """
    Takes base64 image string and returns a 128-d face embedding (np.ndarray)
    Returns None if no face is detected or an error occurs.
    """
    print("Encoder: 1. Processing image string")
    try:
        if "," in image_base64:
            image_base64 = image_base64.split(",")[1]

        print("Encoder: 2. Decoding base64")
        image_bytes = base64.b64decode(image_base64)
        
        print("Encoder: 3. Opening image with PIL")
        image = Image.open(BytesIO(image_bytes)).convert("RGB")
        print(f"Encoder: Original image size: {image.width}x{image.height}")

        # Save the received image for debugging
        try:
            debug_image_path = "debug_image.jpg"
            image.save(debug_image_path, "JPEG")
            print(f"Encoder: Debug image saved to {debug_image_path}")
            
            # Re-load the image from disk to ensure it's clean
            print("Encoder: Reloading debug image from disk")
            image_np = face_recognition.load_image_file(debug_image_path)

        except Exception as e:
            print(f"Encoder: Error saving or reloading debug image: {e}")
            return None
        
        print("Encoder: 4. Detecting face locations")
        face_locations = face_recognition.face_locations(image_np)
        print(f"Encoder: 5. Found {len(face_locations)} face(s)")

        if not face_locations:
            return None

        print("Encoder: 6. Generating face encodings")
        encodings = face_recognition.face_encodings(image_np, face_locations)

        if not encodings:
            print("Encoder: 7. No encodings generated")
            return None
        
        print("Encoder: 8. Returning first encoding")
        return encodings[0].astype(np.float32)

    except Exception as e:
        # Log the error silently for debugging, without crashing
        print(f"Error in generate_embedding: {e}")
        return None