# 🌤️ Weather Agent

A GenAI-powered weather agent that uses function calling to fetch real-time weather information for multiple locations in parallel. Built with OpenAI's Responses API and demonstrates modern agentic AI patterns.

## ✨ Features

- **Parallel Tool Execution**: Fetches weather for multiple cities simultaneously using ThreadPoolExecutor
- **Agentic AI**: Uses OpenAI's Responses API with function calling for intelligent tool usage
- **Multi-turn Conversations**: Maintains conversation history across queries
- **Error Handling**: Robust handling of rate limits, timeouts, and API failures
- **Clean Architecture**: Modular design with separated concerns (schemas, tools, agent logic)

## 🚀 Quick Start

### Prerequisites

- Python 3.14+
- [uv](https://github.com/astral-sh/uv) package manager
- Groq API key (or any OpenAI-compatible API)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/blue0206/weather-agent.git
cd weather-agent
```

2. Create a `.env` file with your API credentials:
```bash
GROQ_API_KEY=your_api_key_here
GROQ_BASE_URL=https://api.groq.com/openai/v1
```

3. Install dependencies:
```bash
uv sync
```

### Usage

Run the agent:
```bash
uv run src/main.py
```

## 💬 Example Interactions

```
> What's the weather in New Delhi?
🛠️ Tool Call: get_weather with {"location":"New Delhi"}
🤖 AI: The weather in New Delhi is: Shallow fog +13°C.

> What's the weather in New Delhi, San Francisco, New York, London, and Bengaluru?
🛠️ Tool Call: get_weather with {"location":"New Delhi"}
🛠️ Tool Call: get_weather with {"location":"San Francisco"}
🛠️ Tool Call: get_weather with {"location":"New York"}
🛠️ Tool Call: get_weather with {"location":"London"}
🛠️ Tool Call: get_weather with {"location":"Bengaluru"}
🤖 AI: The weather in New Delhi is: Shallow fog +13°C. The weather in San Francisco is: Patches of fog +3°C. The weather in New York is: Sunny -3°C. The weather in London is: Overcast +7°C. The weather in Bengaluru is: Mist +20°C.

> exit
🤖 AI: Goodbye! 👋
```

## 🏗️ Architecture

```
weather-agent/
├── src/
│   ├── main.py          # Entry point
│   ├── agent.py         # Agent loop and orchestration
│   ├── tools.py         # Tool definitions and implementations
│   └── schemas.py       # Pydantic schemas for validation
├── tests/
│   ├── test_tools.py    # Unit tests for tools
│   └── test_schemas.py  # Unit tests for schemas
├── .env                 # Environment variables (not in git)
├── pyproject.toml       # Project dependencies
└── README.md
```

### Key Components

- **`agent.py`**: Main agent loop with parallel tool execution using ThreadPoolExecutor
- **`tools.py`**: Weather tool implementation using wttr.in API
- **`schemas.py`**: Pydantic models for type-safe input validation
- **`main.py`**: Simple entry point

## 🔧 Configuration

Environment variables in `.env`:

| Variable | Description | Example |
|----------|-------------|---------|
| `GROQ_API_KEY` | Your API key | `abcd...` |
| `GROQ_BASE_URL` | API base URL | `https://api.groq.com/openai/v1` |

Model configuration in `agent.py`:
- **Model**: `meta-llama/llama-4-scout-17b-16e-instruct`
- **Temperature**: `0.8`
- **Parallel Tool Calls**: `True`

## 🧪 Running Tests

```bash
uv run pytest tests/
```

Run with coverage:
```bash
uv run pytest tests/ --cov=src --cov-report=term-missing
```

## 🛠️ Technical Highlights

### Parallel Tool Execution

The agent uses `ThreadPoolExecutor` to execute multiple weather API calls concurrently:

```python
with ThreadPoolExecutor(max_workers=len(function_calls)) as executor:
    futures = {}
    for item in function_calls:
        future = executor.submit(available_functions[item.name], weather_input)
        futures[future] = item.call_id
    
    for future in as_completed(futures):
        # Process results as they complete
```

### Error Handling

- **Rate Limiting**: Automatic 60-second backoff on 429 errors
- **Timeouts**: 11-second timeout on HTTP requests
- **Graceful Degradation**: Returns error messages instead of crashing

### OpenAI Responses API

Uses the new industry-standard Responses API instead of legacy Chat Completions:

```python
response = client.responses.create(
    model=MODEL_NAME,
    input=message_history,
    tools=tools_schema,
    tool_choice="auto",
    instructions=SYSTEM_PROMPT,
    parallel_tool_calls=True,
)
```

## 📚 Learning Objectives

This project demonstrates:

1. **Agentic AI Patterns**: Tool calling, agent loops, multi-turn conversations
2. **Concurrency**: ThreadPoolExecutor for parallel I/O operations
3. **API Integration**: OpenAI SDK and external REST APIs
4. **Error Handling**: Rate limits, timeouts, network failures
5. **Clean Code**: Type hints, validation, separation of concerns

## 🙏 Acknowledgments

- Uses [Groq](https://groq.com) for fast LLM inference with generous free-tier
- Weather data provided by [wttr.in](https://wttr.in)
- Built with [OpenAI SDK](https://github.com/openai/openai-python)
