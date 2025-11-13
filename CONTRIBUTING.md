# Contributing

Thanks for your interest in contributing to the Snow Leopard Python SDK!

Questions? Reach out on [Discord](https://discord.gg/WGAyr8NpEX)

## Getting Started

### Prerequisites

- Python 3.11 (our default dev version)
- [uv](https://docs.astral.sh/uv/) package manager

### Setup

0. **Fork this repository**
   If you are unfamiliar contributing to open source projects, see [first-contributions](https://github.com/firstcontributions/first-contributions) for a great walkthrough.

1. **Clone your fork**
   ```bash
   git clone https://github.com/SnowLeopard-AI/snowleopard_py.git
   cd snowleopard_py
   ```

2. **Install dependencies**
   ```bash
   uv sync --dev
   ```

3. **Running tests**
   ```bash
   uv run pytest
   ```

### Testing with Different Python Versions

To test against a specific Python version:
```bash
uv run --python 3.10 pytest
```
