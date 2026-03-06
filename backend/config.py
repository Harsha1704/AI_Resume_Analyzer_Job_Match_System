import os

# Base directory of the backend folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# One level up from backend → project root
ROOT_DIR = os.path.dirname(BASE_DIR)

# Datasets folder is at project root level
DATASET_FOLDER = os.path.join(ROOT_DIR, "datasets")

# Models folder is inside backend
MODEL_FOLDER = os.path.join(BASE_DIR, "models")

# Uploads folder is inside backend
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")