import pytest
from pydantic import ValidationError
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from schemas import WeatherInput


class TestWeatherInput:
    """Test cases for WeatherInput schema."""

    def test_valid_location(self):
        """Test that valid location strings are accepted."""
        weather_input = WeatherInput(location="New Delhi")
        assert weather_input.location == "New Delhi"

    def test_location_with_spaces(self):
        """Test that locations with spaces are handled correctly."""
        weather_input = WeatherInput(location="San Francisco")
        assert weather_input.location == "San Francisco"

    def test_location_with_special_characters(self):
        """Test that locations with special characters work."""
        weather_input = WeatherInput(location="São Paulo")
        assert weather_input.location == "São Paulo"

    def test_missing_location_raises_error(self):
        """Test that missing location parameter raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            WeatherInput()

        # Check that the error is about the location field
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("location",) for error in errors)

    def test_location_type_validation(self):
        """Test that non-string location raises validation error."""
        with pytest.raises(ValidationError):
            WeatherInput(location=12345)

    def test_location_case_preservation(self):
        """Test that location case is preserved."""
        weather_input = WeatherInput(location="NeW dElHi")
        assert weather_input.location == "NeW dElHi"

    def test_numeric_string_location(self):
        """Test that numeric strings are accepted as valid locations."""
        weather_input = WeatherInput(location="90210")
        assert weather_input.location == "90210"

    def test_model_dump(self):
        """Test that the model can be serialized to dict."""
        weather_input = WeatherInput(location="London")
        data = weather_input.model_dump()
        assert data == {"location": "London"}

    def test_model_json(self):
        """Test that the model can be serialized to JSON."""
        weather_input = WeatherInput(location="Paris")
        json_str = weather_input.model_dump_json()
        assert "Paris" in json_str
