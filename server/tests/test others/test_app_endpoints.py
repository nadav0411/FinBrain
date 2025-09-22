# test_app_endpoints.py


from flask import jsonify
import app as flask_app


def test_signup_ok(monkeypatch):
    """POST /signup returns 200 when handler succeeds."""

    def fake_signup(data):
        """Fake signup handler."""
        return jsonify({"message": "ok"}), 200

    # Set the fake signup handler
    monkeypatch.setattr(flask_app.logic_connection, "handle_signup", fake_signup)

    # Create a test client
    client = flask_app.app.test_client()

    # Send a POST request to the signup route
    resp = client.post("/signup", json={"email": "a@b.com", "password": "x"})

    # Check if the response is successful
    assert resp.status_code == 200
    assert resp.get_json()["message"] == "ok"


def test_signup_invalid_json():
    """POST /signup returns 400 on invalid JSON."""
    # Create a test client
    client = flask_app.app.test_client()

    # Send a POST request to the signup route
    resp = client.post("/signup", data="not-json", content_type="text/plain")

    # Check if the response is unsuccessful
    assert resp.status_code == 400


def test_login_ok(monkeypatch):
    """POST /login returns 200 when handler succeeds."""

    def fake_login(data):
        """Fake login handler."""
        return jsonify({"message": "logged"}), 200

    # Set the fake login handler
    monkeypatch.setattr(flask_app.logic_connection, "handle_login", fake_login)

    # Create a test client
    client = flask_app.app.test_client()

    # Send a POST request to the login route
    resp = client.post("/login", json={"email": "a@b.com", "password": "x"})

    # Check if the response is successful
    assert resp.status_code == 200
    assert resp.get_json()["message"] == "logged"


def test_logout_ok(monkeypatch):
    """POST /logout returns 200 when handler succeeds and Session-ID is provided."""

    def fake_logout(session_id):
        """Fake logout handler."""
        return jsonify({"message": "logged out", "sid": session_id}), 200

    # Set the fake logout handler
    monkeypatch.setattr(flask_app.logic_connection, "handle_logout", fake_logout)

    # Create a test client
    client = flask_app.app.test_client()

    # Send a POST request to the logout route
    resp = client.post("/logout", headers={"Session-ID": "abc123"})

    # Check if the response is successful
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["message"] == "logged out"
    assert data["sid"] == "abc123"


def test_add_expense_invalid_json():
    """POST /add_expense returns 400 on invalid JSON."""
    # Create a test client
    client = flask_app.app.test_client()

    # Send a POST request to the add expense route
    resp = client.post("/add_expense", data="not-json", content_type="text/plain")

    # Check if the response is unsuccessful
    assert resp.status_code == 400


def test_get_expenses_ok(monkeypatch):
    """GET /get_expenses returns 200 and forwards params to handler."""

    def fake_get(month, year, session_id):
        """Fake get expenses handler."""
        return jsonify({"month": month, "year": year, "sid": session_id, "items": []}), 200

    # Set the fake get expenses handler
    monkeypatch.setattr(flask_app.logic_expenses, "handle_get_expenses", fake_get)

    # Create a test client
    client = flask_app.app.test_client()

    # Send a GET request to the get expenses route
    resp = client.get("/get_expenses?month=1&year=2025", headers={"Session-ID": "sid1"})

    # Check if the response is successful
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["month"] == 1 and data["year"] == 2025 and data["sid"] == "sid1"


def test_expenses_for_dashboard_ok(monkeypatch):
    """GET /expenses_for_dashboard returns 200 with parsed lists and params."""

    def fake_dashboard(chart, currency, months, categories, session_id):
        """Fake get expenses for dashboard handler."""
        return (
            jsonify({
                "chart": chart,
                "currency": currency,
                "months": months,
                "categories": categories,
                "sid": session_id,
            }),
            200,
        )

    # Set the fake get expenses for dashboard handler
    monkeypatch.setattr(flask_app.logic_expenses, "handle_get_expenses_for_dashboard", fake_dashboard)

    # Create a test client
    client = flask_app.app.test_client()

    # Send a GET request to the get expenses for dashboard route
    resp = client.get(
        "/expenses_for_dashboard?chart=pie&currency=USD&months=1&months=2&categories=Food&categories=Transport",
        headers={"Session-ID": "sid2"},
    )

    # Check if the response is successful
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["chart"] == "pie"
    assert data["currency"] == "USD"
    assert data["months"] == ["1", "2"]
    assert data["categories"] == ["Food", "Transport"]
    assert data["sid"] == "sid2"