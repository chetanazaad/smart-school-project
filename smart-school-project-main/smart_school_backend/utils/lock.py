# smart_school_backend/utils/lock.py
import threading

# Global lock to serialize CPU-bound, thread-unsafe C++ dlib calls
# This prevents simultaneous dlib executions from causing C++ segmentation faults.
face_lock = threading.Lock()
