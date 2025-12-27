import requests


def get_weather(city: str) -> str:
    url = f"https://wttr.in/{city.lower()}?format=%C+%t"

    try:
        response = requests.get(url)

        if response.status_code == 200:
            return f"The weather in {city.title()} is: {response.text}"

        return "Something went wrong while fetching the weather."
    except Exception as e:
        return f"Exeption occurred: {str(e)}"


available_tools = {"get_weather": get_weather}
