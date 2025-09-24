# trainer.py

# NOTE: This code has very detailed comments because it's my first time
# learning how to build and use an AI model.


# pandas lets us make a table from lists (It's like working with Excel in code).
# We'll use it to store the descriptions and categories together.
import pandas as pd
# joblib can save and load machine learning models to files.
import joblib
import logging

# scikit-learn -> a library for machine learning.
# TF-IDF turns words into numbers. It gives more importance to unique words in a sentence.
# Example: "buy buy buy coffee" → TF-IDF will care more about "coffee" than repeated "buy".
from sklearn.feature_extraction.text import TfidfVectorizer 
# This is a machine learning model. It learns from data to predict the right category.
from sklearn.linear_model import LogisticRegression


# Create a logger for this module
logger = logging.getLogger(__name__)  


def train_and_save_model():
    """
    This function trains the model and saves it to a file.
    """
    logger.info("Starting model training")
    # This loads the training data from a CSV file.
    # The file contains two columns: 'description' and 'category'.
    # Each row is one example the model will learn from.
    try:
        df = pd.read_csv('finbrain_model/training_data.csv')
        logger.info(f"Training data loaded | rows={len(df)} | columns={list(df.columns)}")
    except Exception as e:
        logger.error(f"Failed to load training data | error={str(e)}")
        raise

    # Create a TF-IDF vectorizer. This will learn which words are important.
    # It turns each sentence into a list of numbers, based on the importance of words.
    # Words that appear often in one sentence but not in others get higher weight.
    vectorizer = TfidfVectorizer()

    # Learn from the text and convert each sentence into a numeric vector.
    # Each row is a sentence, and each column is a word that appeared in the dataset.
    # X is the input data the model will learn from.
    logger.info("Creating TF-IDF vectors from descriptions")
    X = vectorizer.fit_transform(df['description'])  

    # These are the correct answers (labels). The model will try to predict these.
    y = df['category']
    logger.info(f"Training data prepared | features={X.shape[1]} | samples={X.shape[0]}")

    # Create the Logistic Regression model. This is a simple model that works for text classification.
    # max_iter=1000 means "try up to 1000 times to learn" (just in case it's slow to learn).
    # This is where the model "learns" what text belongs to what category.
    model = LogisticRegression(max_iter=1000, solver='lbfgs')
    logger.info("Starting model training with Logistic Regression")

    # Train the model using the input data (X) and correct answers (y).
    model.fit(X, y)
    logger.info("Model training completed") 

    # Save the trained model to a file called model.pkl (to load it later to use it)
    try:
        joblib.dump(model, "finbrain_model/model.pkl")
        logger.info("Model saved successfully | model_path=finbrain_model/model.pkl")
    except Exception as e:
        logger.error(f"Failed to save model | error={str(e)}")
        raise

    # Save the TF-IDF vectorizer to a file too. I MUST use the same vectorizer later for predictions.
    try:
        joblib.dump(vectorizer, "finbrain_model/vectorizer.pkl")
        logger.info("Vectorizer saved successfully | vectorizer_path=finbrain_model/vectorizer.pkl")
    except Exception as e:
        logger.error(f"Failed to save vectorizer | error={str(e)}")
        raise

    # Print a message to show that everything worked
    logger.info("Model and vectorizer saved successfully")
    print("Model and vectorizer saved successfully.")


if __name__ == "__main__":
    train_and_save_model()
