from pydantic import BaseModel, Field


class WeatherInput(BaseModel):
    location: str = Field(
        ..., description="The city name for which the weather is to be retrieved."
    )
