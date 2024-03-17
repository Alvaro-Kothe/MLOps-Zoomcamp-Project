# pylint: disable=duplicate-code
from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient

from src.api import app


class MockModel:
    def predict(self, _):
        return [0.5]


@pytest.fixture(scope="session", autouse=True)
def mock_encoder():
    with patch("src.api.prepare_features", Mock()), patch("src.api.model", MockModel()):
        yield


@pytest.fixture(name="client")
def get_client():
    return TestClient(app)


@pytest.fixture(name="valid_request_data")
def get_valid_request_data():
    return {
        "cap_shape": "x",
        "cap_surface": "s",
        "cap_color": "n",
        "bruises": "t",
        "odor": "a",
        "gill_attachment": "f",
        "gill_spacing": "c",
        "gill_size": "n",
        "gill_color": "b",
        "stalk_shape": "e",
        "stalk_root": "e",
        "stalk_surface_above_ring": "f",
        "stalk_surface_below_ring": "f",
        "stalk_color_above_ring": "b",
        "stalk_color_below_ring": "b",
        "veil_type": "p",
        "veil_color": "n",
        "ring_number": "n",
        "ring_type": "p",
        "spore_print_color": "k",
        "population": "a",
        "habitat": "g",
    }


def test_homepage(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.template.name == "index.html"


def test_predict(valid_request_data, client):
    response = client.post("/predict", data=valid_request_data)
    assert response.status_code == 200
    assert "is 0.5" in response.text


def test_feedback_with_db_undefined(valid_request_data, client):
    with patch("src.api.DATABASE_FILE", None):
        response = client.post("/predict", data=valid_request_data)
        assert response.status_code == 200
        assert '<button type="submit">Submit</button>' not in response.text


def test_feedback_with_db_defined(valid_request_data, client):
    with (
        patch("src.api.DATABASE_FILE"),
        patch("src.api.database"),
    ):
        response = client.post("/predict", data=valid_request_data)
        assert response.status_code == 200
        assert '<button type="submit">Submit</button>' in response.text

        confirm_data = {"confirmation": "yes", "mushroom_classification": 1}

        confirm_response = client.post("/confirm_classification", data=confirm_data)
        assert confirm_response.status_code == 200
        assert '<button type="submit">Submit</button>' not in confirm_response.text
        assert "Form submitted" in confirm_response.text


def test_api(client):
    request_data = {
        "cap_shape": "x",
        "cap_surface": "s",
        "cap_color": "n",
        "bruises": "t",
        "odor": "a",
        "gill_attachment": "f",
        "gill_spacing": "c",
        "gill_size": "n",
        "gill_color": "b",
        "stalk_shape": "e",
        "stalk_root": "e",
        "stalk_surface_above_ring": "f",
        "stalk_surface_below_ring": "f",
        "stalk_color_above_ring": "b",
        "stalk_color_below_ring": "b",
        "veil_type": "p",
        "veil_color": "n",
        "ring_number": "n",
        "ring_type": "e",
        "spore_print_color": "k",
        "population": "a",
        "habitat": "g",
    }

    response = client.post("/api/predict", json=request_data)
    assert response.status_code == 200

    response_json = response.json()
    assert response_json["poisonous-probability"] == 0.5
