# test_predictmodelloader.py


# type: ignore
import os
import sys
import joblib
import importlib
from pathlib import Path
import pytest


def make_dummy_model_files(model_path: Path, vectorizer_path: Path):
    """Create minimal model/vectorizer files for tests."""
    model_path.parent.mkdir(parents=True, exist_ok=True)
    # Create a dummy model file
    joblib.dump({"dummy": True}, os.path.join(model_path.parent, "model.pkl"))
    # Create a dummy vectorizer file
    joblib.dump(["vocab"], os.path.join(vectorizer_path.parent, "vectorizer.pkl"))


def test_import_succeeds_with_files(tmp_path, monkeypatch):
    """Import should succeed when the files exist."""
    workdir = tmp_path
    # Create a temporary finbrain_model folder
    finbrain_dir = os.path.join(workdir, "finbrain_model")
    # Create a dummy model file
    make_dummy_model_files(Path(finbrain_dir) / "model.pkl", Path(finbrain_dir) / "vectorizer.pkl")
    # Make predictmodelloader.py use this temporary directory
    monkeypatch.chdir(workdir)

    # Remove the module from the sys.modules dictionary (because we dont want to use the existing one)
    sys.modules.pop("predictmodelloader", None)
    # Run the import
    module = importlib.import_module("predictmodelloader")

    # Module should expose loaded objects
    assert hasattr(module, "model")
    assert hasattr(module, "vectorizer")


def test_import_fails_without_files(tmp_path, monkeypatch):
    """Import should fail when files are missing."""
    # Create a temporary directory
    workdir = tmp_path
    # Make predictmodelloader.py use this temporary directory
    monkeypatch.chdir(workdir)

    # Remove the module from the sys.modules dictionary (because we dont want to use the existing one)
    sys.modules.pop("predictmodelloader", None)

    # Run the import and expect a FileNotFoundError
    with pytest.raises(FileNotFoundError):
        importlib.import_module("predictmodelloader")
    

def test_pass():
    """
    Test that the test passes (to clean up the test database)
    """
    assert True


