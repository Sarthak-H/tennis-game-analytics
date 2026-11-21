"""
Unit tests for the SportRadar API client and modules.
"""

from unittest.mock import patch, MagicMock

try:
    import pytest
except ImportError:
    class PytestMock:
        class raises:
            def __init__(self, expected_exc):
                self.expected_exc = expected_exc
                self.value = None
            def __enter__(self):
                return self
            def __exit__(self, exc_type, exc_val, exc_tb):
                if exc_type is None:
                    raise AssertionError(f"Expected exception {self.expected_exc} was not raised")
                if issubclass(exc_type, self.expected_exc):
                    self.value = exc_val
                    return True
                return False
    pytest = PytestMock()

from api.sportradar_client import SportRadarClient, SportRadarAPIError
from api.competitions import fetch_competitions_raw
from api.complexes import fetch_complexes_raw
from api.rankings import fetch_doubles_rankings_raw


def test_client_init():
    client = SportRadarClient(api_key="test_key_123")
    assert client.api_key == "test_key_123"
    assert "https://api.sportradar.com" in client.base_url


def test_missing_api_key_raises():
    client = SportRadarClient(api_key="")
    with pytest.raises(SportRadarAPIError) as exc_info:
        client.request("/test_endpoint")
    assert "SportRadar API Key is not configured" in str(exc_info.value)


@patch("requests.Session.get")
def test_successful_request(mock_get):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"competitions": [{"id": "sr:competition:1"}]}
    mock_get.return_value = mock_resp

    client = SportRadarClient(api_key="dummy_key")
    data = client.request("/competitions.json")

    assert "competitions" in data
    assert len(data["competitions"]) == 1


@patch("requests.Session.get")
def test_unauthorized_error(mock_get):
    mock_resp = MagicMock()
    mock_resp.status_code = 401
    mock_resp.text = "Unauthorized"
    mock_get.return_value = mock_resp

    client = SportRadarClient(api_key="wrong_key")
    with pytest.raises(SportRadarAPIError) as exc_info:
        client.request("/competitions.json")
    assert exc_info.value.status_code == 401
    assert "Authentication Failed" in str(exc_info.value)


@patch("requests.Session.get")
def test_fetch_modules(mock_get):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"data": "test"}
    mock_get.return_value = mock_resp

    client = SportRadarClient(api_key="dummy")
    assert fetch_competitions_raw(client) == {"data": "test"}
    assert fetch_complexes_raw(client) == {"data": "test"}
    assert fetch_doubles_rankings_raw(client) == {"data": "test"}
