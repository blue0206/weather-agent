from openai._exceptions import RateLimitError
from schemas import WeatherInput
from dotenv import load_dotenv
from openai import OpenAI
from tools import tools_schema, available_functions
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import os
import json

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_BASE_URL = os.getenv("GROQ_BASE_URL")

if not GROQ_API_KEY or not GROQ_BASE_URL:
    raise ValueError(
        "Missing required environment variables: GROQ_API_KEY and GROQ_BASE_URL"
    )

client = OpenAI(api_key=GROQ_API_KEY, base_url=GROQ_BASE_URL)

MODEL_NAME = "meta-llama/llama-4-scout-17b-16e-instruct"

SYSTEM_PROMPT = """
You are a helpful AI Assistant.
If the user asks for information you don't have (like weather), you can use the available tools.
Don't make up facts.

Available Tools:
get_weather(location: str): A function that returns the current weather for a specific location. It takes a single argument: location (str).

In case user has multiple queries, get answers for them, consolidate the tool outputs and return a single response.

EXAMPLES:
Question: What is the current weather in New Delhi?
Answer: The weather in New Delhi is sunny with a temperature of +21°C.

Question: What is the current weather in New Delhi and San Francisco?
Answer: The weather in New Delhi is sunny with a temperature of +21°C. The weather in San Francisco is rainy with a temperature of +15°C. 
"""


def run() -> None:
    try:
        message_history = []
        while True:
            print("\n")
            user_input = input("> ")

            if user_input.lower() == "exit":
                print("🤖 AI: Goodbye! 👋")
                break

            message_history.append({"role": "user", "content": user_input})

            # Agent Loop
            while True:
                try:
                    response = client.responses.create(
                        model=MODEL_NAME,
                        input=message_history,
                        tools=tools_schema,
                        tool_choice="auto",
                        instructions=SYSTEM_PROMPT,
                        temperature=0.8,
                        parallel_tool_calls=True,
                    )

                    message_history += response.output

                    function_calls = [
                        item for item in response.output if item.type == "function_call"
                    ]

                    if function_calls:
                        with ThreadPoolExecutor(
                            max_workers=len(function_calls)
                        ) as executor:
                            futures = {}

                            for item in function_calls:
                                if item.name == "get_weather":
                                    print(
                                        f"🛠️ Tool Call: {item.name} with {item.arguments}"
                                    )

                                    weather_input = WeatherInput(
                                        **json.loads(item.arguments)
                                    )

                                    future = executor.submit(
                                        available_functions[item.name], weather_input
                                    )
                                    futures[future] = item.call_id
                                else:
                                    print(
                                        f"🛠️ Tool Call: Sorry, I could not call the tool: {item.name}"
                                    )

                            for future in as_completed(futures):
                                call_id = futures[future]
                                try:
                                    weather = future.result()
                                    message_history.append(
                                        {
                                            "type": "function_call_output",
                                            "call_id": call_id,
                                            "output": json.dumps({"weather": weather}),
                                        }
                                    )
                                except Exception as e:
                                    print(f"Error executing tool: {e}")
                                    message_history.append(
                                        {
                                            "type": "function_call_output",
                                            "call_id": call_id,
                                            "output": json.dumps({"error": str(e)}),
                                        }
                                    )
                        continue
                    else:
                        done = False
                        for item in response.output:
                            if item.type != "function_call":
                                if item.content is None:
                                    continue
                                for item_content in item.content:
                                    print(f"🤖 AI: {item_content.text}")
                                    if item_content.type == "output_text":
                                        done = True
                                        break

                        if done:
                            break

                except RateLimitError:
                    print("⚠️ Rate limit hit. Waiting 60 seconds...")
                    time.sleep(60)
                    continue

    except KeyboardInterrupt:
        print("\n🤖 AI: Goodbye! 👋")
    except Exception as e:
        print(f"Unexpected Error: {e}")
        raise
