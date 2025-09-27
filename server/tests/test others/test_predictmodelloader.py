# FinBrain Project - test_predictmodelloader.py - MIT License (c) 2025 Nadav Eshed


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

    # Add the src directory to the path so we can import the module
    # Get the absolute path to the src directory
    test_dir = os.path.dirname(os.path.abspath(__file__))
    src_path = os.path.join(test_dir, '..', '..', 'src')
    src_path = os.path.abspath(src_path)
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
    
    # Remove the module from the sys.modules dictionary (because we dont want to use the existing one)
    modules_to_remove = [key for key in sys.modules.keys() if 'predictmodelloader' in key]
    for module_key in modules_to_remove:
        sys.modules.pop(module_key, None)
    
    # Run the import
    import importlib.util as util
    possible_paths = [
        os.path.join(src_path, "models", "predictmodelloader.py"),
        os.path.join(os.getcwd(), "src", "models", "predictmodelloader.py"),
        os.path.join(os.path.dirname(os.getcwd()), "src", "models", "predictmodelloader.py")
    ]
    
    module_file_path = None
    for path in possible_paths:
        if os.path.exists(path):
            module_file_path = path
            break
    
    if module_file_path is None:
        raise FileNotFoundError(f"Could not find predictmodelloader.py in any of the expected locations: {possible_paths}")
    
    spec = util.spec_from_file_location("predictmodelloader", module_file_path)
    module = util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # Module should expose loaded objects
    assert hasattr(module, "model")
    assert hasattr(module, "vectorizer")


def test_import_fails_without_files(tmp_path, monkeypatch):
    """Import should fail when files are missing."""
    # Create a temporary directory
    workdir = tmp_path
    # Make predictmodelloader.py use this temporary directory
    monkeypatch.chdir(workdir)

    # Add the src directory to the path so we can import the module
    # Get the absolute path to the src directory
    test_dir = os.path.dirname(os.path.abspath(__file__))
    src_path = os.path.join(test_dir, '..', '..', 'src')
    src_path = os.path.abspath(src_path)
    if src_path not in sys.path:
        sys.path.insert(0, src_path)

    # Remove the module from the sys.modules dictionary (because we dont want to use the existing one)
    modules_to_remove = [key for key in sys.modules.keys() if 'predictmodelloader' in key]
    for module_key in modules_to_remove:
        sys.modules.pop(module_key, None)

    # Run the import
    import importlib.util as util
    possible_paths = [
        os.path.join(src_path, "models", "predictmodelloader.py"),
        os.path.join(os.getcwd(), "src", "models", "predictmodelloader.py"),
        os.path.join(os.path.dirname(os.getcwd()), "src", "models", "predictmodelloader.py")
    ]
    
    module_file_path = None
    for path in possible_paths:
        if os.path.exists(path):
            module_file_path = path
            break
    
    if module_file_path is None:
        raise FileNotFoundError(f"Could not find predictmodelloader.py in any of the expected locations: {possible_paths}")

    # Mock os.path.exists to return False for model files
    def mock_exists(path):
        if "model.pkl" in path or "vectorizer.pkl" in path:
            return False
        return os.path.exists(path)
    
    monkeypatch.setattr(os.path, "exists", mock_exists)

    # Run the import and expect a FileNotFoundError
    with pytest.raises(FileNotFoundError):
        spec = util.spec_from_file_location("predictmodelloader", module_file_path)
        module = util.module_from_spec(spec)
        spec.loader.exec_module(module)
    

def test_pass():
    """
    Test that the test passes (to clean up the test database)
    """
    assert True


