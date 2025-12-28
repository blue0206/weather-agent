import requests
from schemas import WeatherInput

def get_weather(input: WeatherInput) -> str:
    location = input.location
    url = f"https://wttr.in/{location.lower()}?format=%C+%t"

    try:
        response = requests.get(url, timeout=11)

        if response.status_code == 200:
            return f"The weather in {location.title()} is: {response.text}"

        return f"Failed to fetch weather for {location.title()}. Status Code: {response.status_code}"
    except Exception as e:
        return f"Exception occurred: {str(e)}"


tools_schema = [
    {
        "type": "function",
        "name": "get_weather",
        "description": "Get the current weather for a specific location.",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The location name for which the weather is to be retrieved."
                },
            },
            "required": ["location"]
        }
    }
]

available_functions = {
    "get_weather": get_weather
}
