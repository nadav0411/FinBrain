# FinBrain Project - predictmodelloader.py - MIT License (c) 2025 Nadav Eshed


import joblib
import os
import logging


# Create a logger for this module
logger = logging.getLogger(__name__)

def resolve_model_paths():
    """
    Tries to locate the trained model and vectorizer across all common environments:
    - Local development
    - Docker / Render
    - GitHub Actions (if model exists locally)
    """
    possible_paths = [
        # Local dev (when running directly)
        os.path.join(os.path.dirname(__file__), "finbrain_model", "model.pkl"),
        # Docker/Render (mounted under /app/src)
        os.path.join("/app/src/models/finbrain_model", "model.pkl"),
        # GitHub Actions or alternate CWD (src/)
        os.path.join(os.getcwd(), "src/models/finbrain_model", "model.pkl"),
        # Fallback if running from root of repo
        os.path.join(os.getcwd(), "server/src/models/finbrain_model", "model.pkl"),
    ]

    for path in possible_paths:
        if os.path.exists(path):
            base_dir = os.path.dirname(path)
            return path, os.path.join(base_dir, "vectorizer.pkl")

    return None, None


# --- GitHub Actions mock mode ---
is_github_actions = os.getenv("GITHUB_ACTIONS", "false").lower() == "true"

if is_github_actions:
    logger.info("Detected GitHub Actions environment — using mock AI model (no .pkl files loaded).")

    class MockModel:
        """A mock classifier used during CI tests (always returns 'Other')."""
        def predict(self, X):
            return ["Other"]

    class MockVectorizer:
        """A mock vectorizer used during CI tests (returns input as-is)."""
        def transform(self, texts):
            return texts

    model = MockModel()
    vectorizer = MockVectorizer()

else:
    # --- Real environment (local, Docker, Render) ---
    model_path, vectorizer_path = resolve_model_paths()
    if not model_path or not vectorizer_path:
        logger.error("Model files not found in any known location.")
        raise FileNotFoundError(
            "Model files not found. I probably need to run trainer.py first to train and save model.pkl/vectorizer.pkl."
        )

    try:
        model = joblib.load(model_path)
        vectorizer = joblib.load(vectorizer_path)
        logger.info(f"Model and vectorizer loaded successfully | model_path={model_path}")
    except Exception as e:
        logger.error(f"Failed to load model/vectorizer | error={str(e)}")
        raise