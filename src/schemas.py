from pydantic import BaseModel, Field
from typing import Optional

class OutputFormat(BaseModel):
    step: str = Field(
        ...,
        description="The id of step. Example: 'PLAN', 'OUTPUT', 'TOOL' or 'START'."
    )
    content: Optional[str] = Field(
        None, 
        description="The content of the step."
    )
    tool: Optional[str] = Field(
        None,
        description="The name of tool used in the step."
    )
    input: Optional[str] = Field(
        None,
        description="The input to the tool used in the step."
    )
    output: Optional[str] = Field(
        None,
        description="The output of the tool used in the step."
    )
