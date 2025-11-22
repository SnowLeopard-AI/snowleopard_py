# SnowLeopard SDK for Python

Python client library for [Snow Leopard Playground](https://try.snowleopard.ai)

## Installation

```bash
pip install snowleopard
```

## Quick Start

```python
from snowleopard import SnowLeopardPlaygroundClient

# Initialize the client (or AsyncSnowLeopardPlaygroundClient)
client = SnowLeopardPlaygroundClient(api_key="your-api-key")

# Query your data in natural language
response = client.retrieve(
    datafile_id="your-datafile-id",
    user_query="How many users signed up last month?"
)
```

## Getting Started

1. **Get your API key** from [https://auth.snowleopard.ai/account/api_keys](https://auth.snowleopard.ai/account/api_keys)
2. **Upload your datafiles** at [https://try.snowleopard.ai](https://try.snowleopard.ai)
3. **Set your API key** via environment variable:
    ```bash
    export SNOWLEOPARD_API_KEY="your-api-key"
    ```
    
    Or pass it directly to the client:
    
    ```python
    SnowLeopardPlaygroundClient(api_key="your-api-key")
    ```

## Usage

### Synchronous Client

```python
from snowleopard import SnowLeopardPlaygroundClient

with SnowLeopardPlaygroundClient() as client:
    # Get data directly from a natural language query
    response = client.retrieve("datafile-id", "What's the total revenue?")
    print(response.data)
    
    # Stream natural language summary of live data
    for chunk in client.response("datafile-id", "Show me top 10 customers"):
        print(chunk)
```

### Async Client

```python
from snowleopard import AsyncSnowLeopardPlaygroundClient

async with AsyncSnowLeopardPlaygroundClient() as client:
    # Get complete results
    response = await client.retrieve("datafile-id", "What's the total revenue?")
    print(response.data)

    # Get streaming results
    async for chunk in client.response("datafile-id", "Show me top 10 customers"):
        print(chunk)
```

### CLI

The SDK includes a command-line interface:

```bash
pip install snowleopard
snowy retrieve <datafile-id> "How many records are there?"
snowy response <datafile-id> "Summarize the data"
```

## Contributing

For SDK developer docs and how to contribute, see [CONTRIBUTING.md](CONTRIBUTING.md)
