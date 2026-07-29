# Snow Leopard SDK for Python

This repo contains the Python client library for [Snow Leopard](https://cloud.snowleopard.ai) APIs.

See our [API documentation](https://docs.snowleopard.ai) for more details.

## Installation

```bash
pip install snowleopard
```

## Quick Start

```python
from snowleopard import SnowLeopardClient

# Initialize the client (or AsyncSnowLeopardClient)
client = SnowLeopardClient(api_key="your-api-key")

# Query your data in natural language
response = client.retrieve(user_query="How many users signed up last month?", instance_id="your-instance-id")
```

## Getting Started

1. **Try Snow Leopard here** [https://cloud.snowleopard.ai](https://cloud.snowleopard.ai)
2. **Set your API key** via environment variable:
    ```bash
    export SNOWLEOPARD_API_KEY="your-api-key"
    ```
    
    Or pass it directly to the client:
    
    ```python
    SnowLeopardClient(api_key="your-api-key")
    ```

## Usage

### Synchronous Client

```python
from snowleopard import SnowLeopardClient

with SnowLeopardClient() as client:
   # Get data directly from a natural language query
   response = client.retrieve(user_query="How many superheroes are there?")
   print(response.data)

   # Stream natural language summary of live data
   for chunk in client.response(user_query="How many superheroes are there?"):
      print(chunk)

   # Give feedback to help Snow Leopard understand your business logic better
   client.feedback(
      feedback_text="The revenue column in the orders table should be labeled "
      "'gross revenue before discounts', not 'net revenue'.",
      instance_id="<instance-id>"
   )
```

### Async Client

```python
from snowleopard import AsyncSnowLeopardClient

async with AsyncSnowLeopardClient() as client:
   # Get complete results
   response = await client.retrieve(user_query="How many superheroes are there?")
   print(response.data)

   # Get streaming results
   async for chunk in client.response(user_query="How many superheroes are there?"):
      print(chunk)

   # Give feedback to help Snow Leopard understand your business logic better
   await client.feedback(
      feedback_text="The revenue column in the orders table should be labeled "
      "'gross revenue before discounts', not 'net revenue'.",
      instance_id="<instance-id>"
   )
```

### CLI

The SDK includes a command-line interface:

```bash
pip install snowleopard
snowy retrieve --instance <instance-id> "How many records are there?"
snowy response --instance <instance-id> "Summarize the data"
snowy feedback --instance <instance-id> "The revenue totals looked wrong"
```

### On-Premises Customers

For our customers who have a separate deployment per dataset, you should declare <url> explicitly when creating a 
client and omit <instance_id> when querying.

Example:
```python
client = SnowLeopardClient(url="https://{your-vm-ip}:{port}", api_key="your-api-key")
response = client.retrieve(user_query="How many users signed up last month?")
```


## Contributing

For SDK developer docs and how to contribute, see [CONTRIBUTING.md](CONTRIBUTING.md)
