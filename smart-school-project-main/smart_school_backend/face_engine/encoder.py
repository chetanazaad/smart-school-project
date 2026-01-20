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
    print("Encoder: --- Starting embedding generation ---")
    try:
        print("Encoder: Step 1: Decoding base64 image...")
        if "," in image_base64:
            image_base64 = image_base64.split(",")[1]

        image_bytes = base64.b64decode(image_base64)
        print(f"Encoder: Step 1 SUCCESS. Decoded {len(image_bytes)} bytes.")

        print("Encoder: Step 2: Opening image with PIL...")
        image = Image.open(BytesIO(image_bytes)).convert("RGB")
        print(f"Encoder: Step 2 SUCCESS. Image opened. Size: {image.size}, Mode: {image.mode}")

        print("Encoder: Step 3: Converting PIL image to numpy array...")
        image_np = np.array(image)
        print(f"Encoder: Step 3 SUCCESS. Numpy array created. Shape: {image_np.shape}, Dtype: {image_np.dtype}")

        print("Encoder: Step 4: Locating faces in the image (using CNN model)...")
        face_locations = face_recognition.face_locations(image_np, model="cnn")
        print("Encoder: Step 4 SUCCESS. face_locations() executed.")

        if not face_locations:
            print("Encoder: No faces detected in image.")
            print("Encoder: --- Embedding generation finished (no face) ---")
            return None
        
        print(f"Encoder: Found {len(face_locations)} face(s). Locations: {face_locations}")

        print("Encoder: Step 5: Encoding faces...")
        encodings = face_recognition.face_encodings(image_np, face_locations)
        print("Encoder: Step 5 SUCCESS. face_encodings() executed.")

        if not encodings:
            print("Encoder: Could not encode face.")
            print("Encoder: --- Embedding generation finished (encoding failed) ---")
            return None
        
        print(f"Encoder: Generated {len(encodings)} encoding(s).")
        
        embedding = encodings[0].astype(np.float32)
        print("Encoder: Step 6: Casting embedding to float32.")
        print("Encoder: --- Embedding generation finished successfully ---")
        return embedding

    except Exception as e:
        print(f"Encoder: AN UNEXPECTED ERROR OCCURRED in generate_embedding: {e}")
        import traceback
        traceback.print_exc()
        print("Encoder: --- Embedding generation finished (with error) ---")
        return None