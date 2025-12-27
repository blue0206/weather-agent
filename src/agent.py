from dotenv import load_dotenv
from openai import OpenAI
from schemas import OutputFormat
from tools import available_tools
import os
import json

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url=os.getenv("GEMINI_BASE_URL")
)

SYSTEM_PROMPT = """
    You are an expert AI Assistant resolving user queries using Chain of Thought.
    You Work on START, PLAN, TOOL, and OUTPUT steps.
    You need to first PLAN what needs to be done. The PLAN can be multiple steps.
    Once enough plan has been done, you can finally give an OUTPUT.
    If you need some information from an external source, you can use the TOOL step.

    IMPORTANT:
    For every tool call, wait for the OBSERVE step which is the output of the called TOOL. This will take some time as it is an API call.
    Do not make another tool call until you get the OBSERVE step.

    Rules:
    - Strictly follow the given JSON output format.
    - Only run one step at a time.
    - The sequence of steps is: START (user input) -> PLAN (can be multiple times) -> TOOL (can be multiple times) -> OUTPUT.
    
    Output JSON Format:
    { "step": "START" | "PLAN" | "TOOL" | "OBSERVE" | "OUTPUT", "content": "string", "tool": "string", "input": "string", "output": "string" }

    Available Tools:
    - get_weather(city: str): Takes city name as input, makes an API call to weather API, and returns the weather.

    Example:
    START: Hey can you tell me the weather in New York?
    PLAN: { "step": "PLAN", "content": "It seems the user is interested in weather of New York." }
    PLAN: { "step": "PLAN", "content": "Let's see if we have a tool to get the weather." }
    PLAN: { "step": "PLAN", "content": "Yes, we have a tool to get the weather. Let's use it." }
    TOOL: { "step": "TOOL", "tool": "get_weather", "input": "New York" }
    OBSERVE: { "step": "OBSERVE", "tool": "get_weather", "input": "New York", "output": "The weather in New York is: 20°C" }
    PLAN: { "step": "PLAN", "content": "Great! I got the weather info about New York!" }
    OUTPUT: { "step": "OUTPUT", "content": "The weather in New York is 20°C" }
"""

message_history = [
    { "role": "system", "content": SYSTEM_PROMPT }
]

def run():
    
    while True:
        print("\n")
        user_input = input("> ")

        if user_input.lower() == "exit":
            break

        message_history.append({ "role": "user", "content": user_input })
        while True:
            response = client.chat.completions.parse(
                model="gemini-2.5-flash",
                messages=message_history,
                response_format=OutputFormat
            )

            result = response.choices[0].message.parsed

            if message_history and message_history[-1]["role"] == "assistant":
                message_history[-1]["content"] += "\n" + json.dumps(result.model_dump())
            else:
                message_history.append({ "role": "assistant", "content": json.dumps(result.model_dump()) })

            if result.step == "START":
                print("START: ", result.content)
                continue
            if result.step == "PLAN":
                print("PLAN: ", result.content)
                continue
            if result.step == "TOOL":
                if result.tool in available_tools:
                    tool_result = available_tools[result.tool](result.input)
                else:
                    tool_result = "Tool not found."
                
                observation_json = json.dumps({
                    "step": "OBSERVE",
                    "tool": result.tool,
                    "input": result.input,
                    "output": tool_result
                })
                
                message_history.append({ "role": "user", "content": observation_json })
                print("OBSERVE: ", tool_result)
                continue
            if result.step == "OUTPUT":
                print("OUTPUT: ", result.content)
                break

