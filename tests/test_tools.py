import pytest
from unittest.mock import Mock, patch
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from tools import get_weather, tools_schema, available_functions
from schemas import WeatherInput


class TestGetWeather:
    """Test cases for get_weather function."""
    
    @patch('tools.requests.get')
    def test_successful_weather_fetch(self, mock_get):
        """Test successful weather data retrieval."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "Sunny +21°C"
        mock_get.return_value = mock_response
        
        weather_input = WeatherInput(location="New Delhi")
        result = get_weather(weather_input)
        
        assert "New Delhi" in result
        assert "Sunny +21°C" in result
        mock_get.assert_called_once()
        
        # Verify timeout is set
        call_kwargs = mock_get.call_args[1]
        assert call_kwargs['timeout'] == 11
    
    @patch('tools.requests.get')
    def test_weather_fetch_with_lowercase_location(self, mock_get):
        """Test that location is converted to lowercase in URL."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "Cloudy +15°C"
        mock_get.return_value = mock_response
        
        weather_input = WeatherInput(location="San Francisco")
        result = get_weather(weather_input)
        
        # Check that the URL uses lowercase
        call_args = mock_get.call_args[0]
        assert "san francisco" in call_args[0].lower()
    
    @patch('tools.requests.get')
    def test_weather_fetch_non_200_status(self, mock_get):
        """Test handling of non-200 status codes."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        weather_input = WeatherInput(location="InvalidCity")
        result = get_weather(weather_input)
        
        assert "Failed to fetch weather" in result
        assert "Invalidcity" in result
        assert "404" in result
    
    @patch('tools.requests.get')
    def test_weather_fetch_timeout(self, mock_get):
        """Test handling of request timeout."""
        from requests.exceptions import Timeout
        mock_get.side_effect = Timeout("Connection timeout")
        
        weather_input = WeatherInput(location="London")
        result = get_weather(weather_input)
        
        assert "Exception occurred" in result
        assert "timeout" in result.lower()
    
    @patch('tools.requests.get')
    def test_weather_fetch_connection_error(self, mock_get):
        """Test handling of connection errors."""
        from requests.exceptions import ConnectionError
        mock_get.side_effect = ConnectionError("Network unreachable")
        
        weather_input = WeatherInput(location="Paris")
        result = get_weather(weather_input)
        
        assert "Exception occurred" in result
    
    @patch('tools.requests.get')
    def test_weather_fetch_generic_exception(self, mock_get):
        """Test handling of generic exceptions."""
        mock_get.side_effect = Exception("Unexpected error")
        
        weather_input = WeatherInput(location="Tokyo")
        result = get_weather(weather_input)
        
        assert "Exception occurred" in result
        assert "Unexpected error" in result
    
    @patch('tools.requests.get')
    def test_location_title_case_in_response(self, mock_get):
        """Test that location is title-cased in the response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "Rainy +10°C"
        mock_get.return_value = mock_response
        
        weather_input = WeatherInput(location="new york")
        result = get_weather(weather_input)
        
        assert "New York" in result  # Should be title-cased
        assert "new york" not in result


class TestToolsSchema:
    """Test cases for tools_schema configuration."""
    
    def test_tools_schema_structure(self):
        """Test that tools_schema has correct structure."""
        assert isinstance(tools_schema, list)
        assert len(tools_schema) == 1
        
        tool = tools_schema[0]
        assert tool["type"] == "function"
        assert tool["name"] == "get_weather"
        assert "description" in tool
        assert "parameters" in tool
    
    def test_tools_schema_parameters(self):
        """Test that tool parameters are correctly defined."""
        tool = tools_schema[0]
        params = tool["parameters"]
        
        assert params["type"] == "object"
        assert "properties" in params
        assert "location" in params["properties"]
        assert params["required"] == ["location"]
    
    def test_tools_schema_location_property(self):
        """Test location property definition."""
        tool = tools_schema[0]
        location_prop = tool["parameters"]["properties"]["location"]
        
        assert location_prop["type"] == "string"
        assert "description" in location_prop


class TestAvailableFunctions:
    """Test cases for available_functions mapping."""
    
    def test_available_functions_contains_get_weather(self):
        """Test that get_weather is in available_functions."""
        assert "get_weather" in available_functions
        assert callable(available_functions["get_weather"])
    
    def test_available_functions_mapping(self):
        """Test that the mapping points to the correct function."""
        assert available_functions["get_weather"] == get_weather
    
    @patch('tools.requests.get')
    def test_available_functions_callable(self, mock_get):
        """Test that functions in the mapping are callable."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "Clear +25°C"
        mock_get.return_value = mock_response
        
        weather_input = WeatherInput(location="Mumbai")
        result = available_functions["get_weather"](weather_input)
        
        assert isinstance(result, str)
        assert "Mumbai" in result
