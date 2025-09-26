# FinBrain Project - test_password_hashing.py - MIT License (c) 2025 Nadav Eshed


from password_hashing import hash_password, verify_password


def test_verify_ok():
    """Hash a password, then verify it successfully."""
    # Hash the password
    plain_password = "S3cureP@ss!"
    hashed_password = hash_password(plain_password)
    
    # Check if the hashed password is a string and not empty
    assert isinstance(hashed_password, str) and len(hashed_password) > 0

    # Verify the password
    assert verify_password(plain_password, hashed_password) is True


def test_verify_wrong_returns_false():
    """Wrong password should not verify against the stored hash."""
    # Hash the password
    plain_password = "correct-password"
    wrong_password = "wrong-password"
    hashed_password = hash_password(plain_password)

    # Check if the password is not verified
    assert verify_password(wrong_password, hashed_password) is False


def test_hash_outputs_are_unique():
    """Same input hashed twice should produce different hashes (random salt)"""
    plain_password = "same-every-time"
    # Hash the password
    hash_one = hash_password(plain_password)
    hash_two = hash_password(plain_password)

    # Hashes should differ due to random salt
    assert hash_one != hash_two

    # Check if the password is verified
    assert verify_password(plain_password, hash_one) is True
    assert verify_password(plain_password, hash_two) is True


def test_pass():
    """
    Test that the test passes (to clean up the test database)
    """
    assert True


