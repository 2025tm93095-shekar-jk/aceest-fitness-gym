import pytest
from app import app, init_db


@pytest.fixture
def client(monkeypatch, tmp_path):
    """Create a separate temporary database for each test."""
    monkeypatch.setattr("app.DB_PATH", str(tmp_path / "test.db"))
    init_db()

    app.config["TESTING"] = True

    with app.test_client() as test_client:
        yield test_client


def create_test_client(client, name="Test User"):
    """Helper to register a client."""
    return client.post("/clients", json={
        "name": name,
        "age": 25,
        "weight": 80,
        "program": "fat_loss"
    })


# -----------------------------------------
# 1. HOME PAGE TESTS
# -----------------------------------------

def test_home(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "Welcome" in response.get_json()["message"]


# -----------------------------------------
# 2. FITNESS PROGRAM TESTS
# -----------------------------------------

def test_list_programs(client):
    response = client.get("/programs")
    assert response.status_code == 200

    data = response.get_json()
    assert "fat_loss" in data
    assert "muscle_gain" in data
    assert "beginner" in data


def test_get_valid_program(client):
    response = client.get("/programs/fat_loss")
    assert response.status_code == 200
    assert response.get_json()["calorie_factor"] == 22


def test_get_invalid_program(client):
    response = client.get("/programs/invalid")
    assert response.status_code == 404


# -----------------------------------------
# 3. CLIENT REGISTRATION TESTS
# -----------------------------------------

def test_create_client(client):
    response = create_test_client(client)

    assert response.status_code == 201
    assert response.get_json()["calories"] == 1760


def test_duplicate_client(client):
    create_test_client(client)

    response = create_test_client(client)
    assert response.status_code == 409


def test_invalid_client_name(client):
    response = client.post("/clients", json={
        "name": "",
        "age": 25,
        "weight": 80,
        "program": "fat_loss"
    })

    assert response.status_code == 400


def test_invalid_client_program(client):
    response = client.post("/clients", json={
        "name": "Invalid Program User",
        "age": 25,
        "weight": 80,
        "program": "unknown"
    })

    assert response.status_code == 400


def test_invalid_client_weight(client):
    response = client.post("/clients", json={
        "name": "Invalid Weight User",
        "age": 25,
        "weight": -10,
        "program": "fat_loss"
    })

    assert response.status_code == 400


# -----------------------------------------
# 4. PROGRESS TRACKING TESTS
# -----------------------------------------

def test_save_progress(client):
    create_test_client(client)

    response = client.post("/clients/Test%20User/progress", json={
        "week": "2026-W41",
        "adherence": 85
    })

    assert response.status_code == 201
    assert response.get_json()["adherence"] == 85


def test_invalid_adherence(client):
    create_test_client(client)

    response = client.post("/clients/Test%20User/progress", json={
        "week": "2026-W41",
        "adherence": 120
    })

    assert response.status_code == 400


def test_progress_unknown_client(client):
    response = client.post("/clients/Unknown/progress", json={
        "week": "2026-W41",
        "adherence": 80
    })

    assert response.status_code == 404


# -----------------------------------------
# 5. WORKOUT LOGGING TESTS
# -----------------------------------------

def test_add_workout(client):
    create_test_client(client)

    response = client.post("/workouts", json={
        "client_name": "Test User",
        "date": "2026-10-11",
        "workout_type": "Strength Training",
        "duration_min": 45,
        "notes": "Back and biceps"
    })

    assert response.status_code == 201

    data = response.get_json()
    assert data["workout_type"] == "Strength Training"
    assert data["duration_min"] == 45
    assert data["id"] > 0


def test_invalid_workout_date(client):
    create_test_client(client)

    response = client.post("/workouts", json={
        "client_name": "Test User",
        "date": "invalid-date",
        "workout_type": "Cardio",
        "duration_min": 30
    })

    assert response.status_code == 400


def test_invalid_workout_duration(client):
    create_test_client(client)

    response = client.post("/workouts", json={
        "client_name": "Test User",
        "date": "2026-10-11",
        "workout_type": "Cardio",
        "duration_min": -5
    })

    assert response.status_code == 400


def test_workout_unknown_client(client):
    response = client.post("/workouts", json={
        "client_name": "Unknown",
        "date": "2026-10-11",
        "workout_type": "Cardio",
        "duration_min": 30
    })

    assert response.status_code == 404


# -----------------------------------------
# 6. MEMBERSHIP TRACKING TESTS
# -----------------------------------------

def test_update_membership(client):
    create_test_client(client)

    response = client.put("/clients/Test%20User/membership", json={
        "membership_expiry": "2099-12-31"
    })

    assert response.status_code == 200

    data = response.get_json()
    assert data["membership_expiry"] == "2099-12-31"
    assert data["status"] == "Active"


def test_get_membership(client):
    create_test_client(client)

    client.put("/clients/Test%20User/membership", json={
        "membership_expiry": "2099-12-31"
    })

    response = client.get("/clients/Test%20User/membership")

    assert response.status_code == 200
    assert response.get_json()["status"] == "Active"


def test_expired_membership(client):
    create_test_client(client)

    response = client.put("/clients/Test%20User/membership", json={
        "membership_expiry": "2020-01-01"
    })

    assert response.status_code == 200
    assert response.get_json()["status"] == "Expired"


def test_invalid_membership_date(client):
    create_test_client(client)

    response = client.put("/clients/Test%20User/membership", json={
        "membership_expiry": "invalid-date"
    })

    assert response.status_code == 400


def test_membership_unknown_client(client):
    response = client.get("/clients/Unknown/membership")
    assert response.status_code == 404
