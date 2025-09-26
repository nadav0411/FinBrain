# FinBrain Project - predictmodelloader.py - MIT License (c) 2025 Nadav Eshed


# NOTE: This code has very detailed comments because it's my first time
# learning how to load a trained model.

# joblib lets us load models and tools we saved earlier.
import joblib
# os helps us check if files exist on the computer.
import os
import logging


# Create a logger for this module
logger = logging.getLogger(__name__)   

# These are the file paths where the model and vectorizer are saved
model_path = "finbrain_model/model.pkl"
vectorizer_path = "finbrain_model/vectorizer.pkl"

# First, we check if both files exist in the folder
# If they do, we load them and use them later
if os.path.exists(model_path) and os.path.exists(vectorizer_path):
    try:
        # Load the trained model from file (this is the AI brain).
        model = joblib.load(model_path)
        logger.info(f"Model loaded successfully | model_path={model_path}")

        # Load the TF-IDF vectorizer from file (this turns text into numbers).
        vectorizer = joblib.load(vectorizer_path)
        logger.info(f"Vectorizer loaded successfully | vectorizer_path={vectorizer_path}")
    except Exception as e:
        logger.error(f"Failed to load model files | model_path={model_path} | vectorizer_path={vectorizer_path} | error={str(e)}")
        raise
else:
    # If the files don't exist, stop and show an error
    logger.error(f"Model files not found | model_path={model_path} | vectorizer_path={vectorizer_path}")
    raise FileNotFoundError("Model files not found. You need to run trainer.py first to train the model.")
