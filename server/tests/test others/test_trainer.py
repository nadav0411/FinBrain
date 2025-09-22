# test_trainer.py


# type: ignore
import os
import csv
import joblib
from pathlib import Path
import pytest
from trainer import train_and_save_model


def write_training_data_csv(file_path, headers, rows):
    """Create a CSV file with the given headers and rows."""
    # Convert to Path object if it's a string
    path = Path(file_path)
    # Create the parent directory if it doesn't exist
    path.parent.mkdir(parents=True, exist_ok=True)
    # Open the file and write the headers and rows
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)


def test_creates_model_files(tmp_path, monkeypatch):
    """
    Train on a tiny dataset and make sure model files are created and loadable.
    """
    # Create a temporary finbrain_model folder with a tiny CSV
    workdir = tmp_path
    finbrain_dir = os.path.join(workdir, "finbrain_model")
    data_csv = os.path.join(finbrain_dir, "training_data.csv")
    # Create a CSV file with the given headers and rows
    write_training_data_csv(
        data_csv,
        ["description", "category"],
        [
            ["coffee at starbucks", "Food & Drinks"],
            ["uber ride", "Transportation"],
            ["monthly netflix subscription", "Leisure & Gifts"],
        ],
    )

    # Make trainer.py use this temporary directory
    monkeypatch.chdir(workdir)

    # Run training
    train_and_save_model()

    # Files should exist and be valid
    model_path = os.path.join(finbrain_dir, "model.pkl")
    vectorizer_path = os.path.join(finbrain_dir, "vectorizer.pkl")
    assert os.path.exists(model_path), "model.pkl was not created"
    assert os.path.exists(vectorizer_path), "vectorizer.pkl was not created"

    # Can load them back
    joblib.load(model_path)
    joblib.load(vectorizer_path)


def test_missing_columns_raises(tmp_path, monkeypatch):
    """
    Make sure training fails if CSV is missing required columns.
    """
    # CSV is missing required columns 'description' and 'category'
    workdir = tmp_path
    finbrain_dir = os.path.join(workdir, "finbrain_model")
    data_csv = os.path.join(finbrain_dir, "training_data.csv")
    # Create a CSV file with the given headers and rows
    write_training_data_csv(
        data_csv,
        # wrong headers on purpose
        ["text", "label"],
        [["coffee at starbucks", "Food & Drinks"]],
    )

    # Make trainer.py use this temporary directory
    monkeypatch.chdir(workdir)

    # Expect KeyError for missing 'description'/'category'
    with pytest.raises(KeyError):
        train_and_save_model()


def test_missing_file_raises_no_files(tmp_path, monkeypatch):
    """
    Make sure training fails if CSV is missing.
    """
    # Do not create training_data.csv
    workdir = tmp_path
    finbrain_dir = os.path.join(workdir, "finbrain_model")
    # Make trainer.py use this temporary directory
    monkeypatch.chdir(workdir)

    # Expect FileNotFoundError when CSV is missing
    with pytest.raises(FileNotFoundError):
        train_and_save_model()

    # No files should be created
    assert not os.path.exists(os.path.join(finbrain_dir, "model.pkl"))
    assert not os.path.exists(os.path.join(finbrain_dir, "vectorizer.pkl"))

