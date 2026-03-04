import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
DATASET_FOLDER = os.path.join(BASE_DIR, "../datasets")
MODEL_FOLDER = os.path.join(BASE_DIR, "models")

ALLOWED_EXTENSIONS = {"pdf"}