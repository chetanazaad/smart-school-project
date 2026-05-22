import base64
import numpy as np
from io import BytesIO
from PIL import Image
import os
import logging
import traceback

# Using face_recognition library instead of DeepFace
# face_recognition uses dlib's ResNet model to generate 128-d face embeddings
# This avoids the TensorFlow dependency issue

logger = logging.getLogger(__name__)

def generate_embedding(image_base64: str):
    """
    Takes a base64 image string and returns a face embedding using face_recognition.
    Returns None if no face is detected or an error occurs.
    """
    try:
        logger.info("Starting face embedding generation...")
        
        if not image_base64:
            logger.error("Empty image_base64 provided")
            return None
            
        # Handle data URL format (e.g., "data:image/jpeg;base64,...")
        if "," in image_base64:
            image_base64 = image_base64.split(",")[1]

        # Decode base64 to bytes
        try:
            image_bytes = base64.b64decode(image_base64)
            logger.info(f"Decoded image bytes: {len(image_bytes)} bytes")
        except Exception as e:
            logger.error(f"Failed to decode base64: {e}")
            return None

        # Debug image saving - enable with environment variable
        if os.getenv("SAVE_DEBUG_IMAGES") == "1":
            try:
                debug_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "debug")
                os.makedirs(debug_dir, exist_ok=True)
                debug_path = os.path.join(debug_dir, "last_input.jpg")
                with open(debug_path, "wb") as df:
                    df.write(image_bytes)
                logger.info(f"Saved debug image to {debug_path}")
            except Exception as e:
                logger.warning(f"Failed to save debug image: {e}")

        # Import face_recognition
        try:
            import face_recognition
            logger.info("face_recognition imported successfully")
        except ImportError as import_err:
            logger.error(f"face_recognition import error: {import_err}")
            return None

        # Convert bytes to PIL Image
        try:
            image = Image.open(BytesIO(image_bytes)).convert("RGB")
        except Exception as e:
            logger.error(f"Failed to convert image bytes to PIL Image: {e}")
            return None

        # Resize large images to speed up and stabilize face detection
        try:
            max_size = 800
            w, h = image.size
            if w > max_size or h > max_size:
                if w > h:
                    new_w = max_size
                    new_h = int(h * (max_size / w))
                else:
                    new_h = max_size
                    new_w = int(w * (max_size / h))
                logger.info(f"Resizing large image from {w}x{h} to {new_w}x{new_h}")
                resampling_method = Image.Resampling.LANCZOS if hasattr(Image, "Resampling") else Image.ANTIALIAS
                image = image.resize((new_w, new_h), resampling_method)
        except Exception as e:
            logger.warning(f"Failed to resize image (will proceed with original): {e}")

        from PIL import ImageOps, ImageEnhance
        
        # We will try a series of face detection strategies with fallback
        image_np = np.array(image)
        face_locations = []
        detection_method = "default"

        try:
            from smart_school_backend.utils.lock import face_lock
        except ImportError:
            from utils.lock import face_lock

        with face_lock:
            # 1. Try standard HOG detection
            try:
                face_locations = face_recognition.face_locations(image_np, number_of_times_to_upsample=1)
                if face_locations:
                    detection_method = "default HOG"
            except Exception as e:
                logger.error(f"Error during face location: {e}")

            # 2. Try with upsampling = 2 (detects smaller faces)
            if not face_locations:
                try:
                    logger.info("Default face detection failed, trying upsampling=2...")
                    face_locations = face_recognition.face_locations(image_np, number_of_times_to_upsample=2)
                    if face_locations:
                        detection_method = "upsampling x2"
                except Exception as e:
                    logger.error(f"Error during face location (upsampling): {e}")

            # 3. Try contrast equalization (fixes bad/uneven lighting)
            if not face_locations:
                try:
                    logger.info("Trying contrast equalization...")
                    equalized_image = ImageOps.equalize(image)
                    image_np = np.array(equalized_image)
                    face_locations = face_recognition.face_locations(image_np, number_of_times_to_upsample=1)
                    if face_locations:
                        detection_method = "contrast equalization"
                    else:
                        # 4. Try equalized + upsampling = 2
                        logger.info("Trying contrast equalization + upsampling=2...")
                        face_locations = face_recognition.face_locations(image_np, number_of_times_to_upsample=2)
                        if face_locations:
                            detection_method = "contrast equalization + upsampling x2"
                except Exception as e:
                    logger.error(f"Error during face location (equalization): {e}")

            # 5. Try contrast enhancement
            if not face_locations:
                try:
                    logger.info("Trying contrast enhancement...")
                    enhancer = ImageEnhance.Contrast(image)
                    enhanced_image = enhancer.enhance(1.5)
                    image_np = np.array(enhanced_image)
                    face_locations = face_recognition.face_locations(image_np, number_of_times_to_upsample=1)
                    if face_locations:
                        detection_method = "contrast enhancement"
                except Exception as e:
                    logger.error(f"Error during face location (contrast enhancement): {e}")

            if not face_locations:
                logger.warning("No face detected in the image - image may be too blurry or face not visible after all attempts")
                return None

            logger.info(f"Face detected using {detection_method} at locations: {face_locations}")

            # Get face encodings using the detected face locations
            try:
                encodings = face_recognition.face_encodings(image_np, known_face_locations=face_locations)
                logger.info(f"Found {len(encodings)} face encoding(s) in the image")
            except Exception as e:
                logger.error(f"Error during face encoding: {e}")
                logger.error(traceback.format_exc())
                return None

            if len(encodings) == 0:
                logger.warning("No face encoding generated")
                return None

            # Get the first face encoding
            embedding = encodings[0]
        
        # Ensure the embedding is a numpy array of float32
        embedding_np = np.array(embedding, dtype=np.float32)

        logger.info(f"Generated embedding with shape: {embedding_np.shape}, dtype: {embedding_np.dtype}")
        return embedding_np

    except Exception as e:
        logger.error(f"Error generating embedding: {type(e).__name__}: {e}")
        logger.error(traceback.format_exc())
        return None
