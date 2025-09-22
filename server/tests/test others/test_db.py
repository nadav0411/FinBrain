# test_db.py


import db


def test_collections_are_usable():
    """Make sure users and expenses collections can be used for basic operations."""
    # Insert a dummy user
    dummy_user = {"email": "test@example.com", "name": "Test User"}
    result = db.users_collection.insert_one(dummy_user)
    assert result.inserted_id is not None
    
    # Insert a dummy expense
    dummy_expense = {"user_email": "test@example.com", "amount": 10.50, "description": "Test expense"}
    result = db.expenses_collection.insert_one(dummy_expense)
    assert result.inserted_id is not None
    
    # Clean up - delete the dummy documents
    db.users_collection.delete_one({"email": "test@example.com"})
    db.expenses_collection.delete_one({"user_email": "test@example.com"})

def test_pass():
    """
    Test that the test passes (to clean up the test database)
    """
    assert True