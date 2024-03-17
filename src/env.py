import os

from dotenv import load_dotenv

load_dotenv()

TOP_N = int(os.getenv("TOP_N", "5"))
EXPERIMENT_NAME = os.getenv("EXPERIMENT_NAME", "mushroom-classification")
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://127.0.0.1:5000")
NUM_TRIALS = int(os.getenv("NUM_TRIALS") or 10)
ENCODER_PATH = os.getenv("ENCODER_PATH", "models/enc.pkl")
LOCAL_MODEL_PATH = os.getenv("LOCAL_MODEL_PATH", "models/model.pkl")
USE_MLFLOW = os.getenv("USE_MLFLOW", "false").lower() in ("true", "t", "1")
DATABASE_FILE = os.getenv("DATABASE_FILE") or None
