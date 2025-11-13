# Generation API Examples

This directory contains examples demonstrating how to use Sotopia with various LLM providers, including local models and cloud APIs.

## Overview

Sotopia uses [LiteLLM](https://github.com/BerriAI/litellm) under the hood, which provides a unified interface to 100+ LLM providers. This means you can easily switch between different models and providers with minimal code changes.

## Examples

### Cloud-based Models

For cloud-based models like OpenAI, Anthropic, Together AI, etc., you can use the model name directly:

```python
model_name="gpt-4o"                    # OpenAI
model_name="claude-3-5-sonnet-20241022" # Anthropic
model_name="together_ai/meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo"  # Together AI
```

Make sure to set the appropriate API keys as environment variables:
- `OPENAI_API_KEY` for OpenAI models
- `ANTHROPIC_API_KEY` for Anthropic models
- `TOGETHER_API_KEY` for Together AI models

### Local Models

#### 1. Ollama (`ollama_model.py`)

[Ollama](https://ollama.ai) is the easiest way to run LLMs locally.

**Setup:**
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull a model
ollama pull llama3.2:1b

# Run the example
uv run python examples/generation_api/ollama_model.py
```

**Usage in code:**
```python
# Default (uses Ollama's default port)
model_name="ollama/llama3.2:1b"

# With custom URL
model_name="ollama/llama3.2:1b@http://localhost:11434"

# With environment variable
export OLLAMA_BASE_URL="http://localhost:11434"
model_name="ollama/llama3.2:1b"
```

#### 2. LM Studio (`lmstudio_model.py`)

[LM Studio](https://lmstudio.ai) provides a user-friendly desktop app for running LLMs.

**Setup:**
1. Download and install LM Studio
2. Download a model in the app
3. Start the local server (default port: 1234)
4. Run the example

```bash
uv run python examples/generation_api/lmstudio_model.py
```

**Usage in code:**
```python
# Default (uses LM Studio's default port)
model_name="lmstudio/local-model"

# With custom URL
model_name="lmstudio/llama-3.2-1b@http://localhost:1234/v1"

# With environment variable
export LMSTUDIO_BASE_URL="http://localhost:1234/v1"
model_name="lmstudio/local-model"
```

#### 3. Generic Local Models (`local_model.py`)

For other OpenAI-compatible local servers (vLLM, LocalAI, FastChat, etc.)

**Setup with vLLM:**
```bash
# Install vLLM
pip install vllm

# Start the server
python -m vllm.entrypoints.openai.api_server \
  --model meta-llama/Llama-3.2-1B \
  --port 8000

# Run the example
uv run python examples/generation_api/local_model.py
```

**Usage in code:**
```python
# Default (uses localhost:8000)
model_name="local/meta-llama/Llama-3.2-1B"

# With custom URL
model_name="local/meta-llama/Llama-3.2-1B@http://localhost:8000/v1"

# With environment variable
export LOCAL_MODEL_BASE_URL="http://localhost:8000/v1"
export LOCAL_MODEL_API_KEY="your-key-if-needed"
model_name="local/meta-llama/Llama-3.2-1B"
```

#### 4. Custom Models (`custom_model.py`)

For LiteLLM proxy servers or other custom OpenAI-compatible endpoints.

**Setup:**
```bash
# Example with LiteLLM proxy
litellm --model ollama/llama3.2:1b --port 8000

# Run the example
uv run python examples/generation_api/custom_model.py
```

**Usage in code:**
```python
# Must include URL
model_name="custom/llama3.2:1b@http://localhost:8000/v1"

# Set API key if needed
export CUSTOM_API_KEY="your-api-key"
```

## Model Format Summary

| Provider | Format | Default URL | API Key Env Var |
|----------|--------|-------------|-----------------|
| Ollama | `ollama/<model>` or `ollama/<model>@<url>` | LiteLLM default | `OLLAMA_API_KEY` |
| LM Studio | `lmstudio/<model>` or `lmstudio/<model>@<url>` | `http://localhost:1234/v1` | `LMSTUDIO_API_KEY` |
| Local | `local/<model>` or `local/<model>@<url>` | `http://localhost:8000/v1` | `LOCAL_MODEL_API_KEY` |
| Custom | `custom/<model>@<url>` | N/A (required) | `CUSTOM_API_KEY` |

## Environment Variables

You can configure the base URL for each provider using environment variables:

```bash
# Ollama
export OLLAMA_BASE_URL="http://localhost:11434"
export OLLAMA_API_KEY="optional-key"

# LM Studio
export LMSTUDIO_BASE_URL="http://localhost:1234/v1"
export LMSTUDIO_API_KEY="lm-studio"

# Generic Local Models
export LOCAL_MODEL_BASE_URL="http://localhost:8000/v1"
export LOCAL_MODEL_API_KEY="local"

# Custom Models
export CUSTOM_API_KEY="your-api-key"
```

## Tips

1. **Performance**: Local models are great for development and privacy, but cloud models typically offer better performance for production use.

2. **Model Selection**: Choose model size based on your hardware:
   - Small models (1B-3B params): Run on most laptops
   - Medium models (7B-13B params): Need good GPU
   - Large models (30B+ params): Need high-end hardware

3. **Structured Output**: Some local models may not support structured output. If you encounter issues, set `structured_output=False` in `agenerate()`.

4. **Debugging**: Set logging level to see detailed API calls:
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

## Troubleshooting

### Connection Refused
- Make sure the local server is running
- Check the port number matches your configuration
- Verify firewall settings

### Model Not Found
- For Ollama: Run `ollama list` to see available models
- For LM Studio: Check the model is loaded in the UI
- For vLLM/others: Verify the model name matches the server config

### Out of Memory
- Try a smaller model
- Reduce context length
- Close other applications

## More Information

- [Sotopia Documentation](https://docs.sotopia.world)
- [LiteLLM Documentation](https://docs.litellm.ai)
- [Ollama Documentation](https://ollama.ai/docs)
- [LM Studio Documentation](https://lmstudio.ai/docs)
