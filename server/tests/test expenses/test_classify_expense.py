# test_classify_expense.py


import logicexpenses as le


def test_classify_expense():
    """
    Test that the classify_expense function returns a string and that the string is in the categories list
    """
    result = le.classify_expense("Bought medicine")
    assert isinstance(result, str)
    assert result in le.categories


def test_classify_expense_invalid_input():
    """
    Test that the classify_expense function returns "other" if the input is invalid
    """
    result = le.classify_expense(123)
    assert result == "other"


def test_classify_expense_empty_input():
    """
    Test that the classify_expense function returns "other" if the input is empty
    """
    result = le.classify_expense("")
    assert result == "other"


def test_classify_expense_none_input():
    """
    Test that the classify_expense function returns "other" if the input is None
    """
    result = le.classify_expense(None)
    assert result == "other"


def test_classify_expense_whitespace_only():
    """
    Test that the classify_expense function returns "other" if the input is only whitespace
    """
    result = le.classify_expense("   ")
    assert result == "other"


def test_classify_expense_tab_and_newline():
    """
    Test that the classify_expense function returns "other" if the input is only tabs and newlines
    """
    result = le.classify_expense("\t\n\r")
    assert result == "other"


def test_classify_expense_boolean_input():
    """
    Test that the classify_expense function returns "other" for boolean input
    """
    result = le.classify_expense(True)
    assert result == "other"
    
    result = le.classify_expense(False)
    assert result == "other"


def test_classify_expense_returns_valid_category():
    """
    Test that the classify_expense function always returns a valid category from the predefined list
    """
    test_cases = [
        "Bought medicine",
        "Paid rent",
        "Gas for car",
        "Bought groceries",
        "Movie ticket",
        "Gym membership"
    ]
    
    for test_case in test_cases:
        result = le.classify_expense(test_case)
        assert result in le.categories, f"Expected result to be in categories, got: {result} for input: {test_case}"


def test_classify_expense_consistency():
    """
    Test that the classify_expense function returns consistent results for the same input
    """
    test_input = "Bought medicine"
    result1 = le.classify_expense(test_input)
    result2 = le.classify_expense(test_input)
    assert result1 == result2, "Function should return consistent results for the same input"


def test_pass():
    """
    Test that the test passes (to clean up the test database)
    """
    assert True