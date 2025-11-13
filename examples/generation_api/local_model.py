# Example: Generate (2~7) random numbers using local models with OpenAI-compatible API
# To run this example:
# This example demonstrates using any local model server with OpenAI-compatible API
# Examples include: vLLM, LocalAI, FastChat, Text Generation WebUI, etc.
#
# 1. Start your local model server (e.g., vLLM):
#        python -m vllm.entrypoints.openai.api_server --model meta-llama/Llama-3.2-1B --port 8000
# 2. Run this example:
#        uv run python examples/generation_api/local_model.py
#
# Local models can be used in three ways:
# 1. Direct model name: "local/model-name" (uses default URL http://localhost:8000/v1)
# 2. With custom URL: "local/model-name@http://localhost:8000/v1"
# 3. With environment variable: Set LOCAL_MODEL_BASE_URL="http://localhost:8000/v1"
#
# You can also set LOCAL_MODEL_API_KEY if your local server requires authentication
#
# Expected output: a bunch of logs and an output like [[14, 7], [14, 7, 3], [14, 7, 3, 9], [14, 7, 3, 9, 6], [14, 7, 3, 9, 6, 8]]

from sotopia.generation_utils import ListOfIntOutputParser, agenerate
import logging
import asyncio
import os

# Set logging to the lowest level to show all logs
logging.basicConfig(level=0)


async def generate_n_random_numbers_default(n: int) -> list[int]:
    """Generate n random numbers using local model with default settings."""
    return await agenerate(
        model_name="local/meta-llama/Llama-3.2-1B",
        template="Generate {n} random integer numbers. {format_instructions}",
        input_values={"n": str(n)},
        temperature=0.0,
        output_parser=ListOfIntOutputParser(n),
    )


async def generate_with_custom_url(n: int) -> list[int]:
    """Generate n random numbers using local model with custom URL."""
    return await agenerate(
        model_name="local/meta-llama/Llama-3.2-1B@http://localhost:8000/v1",
        template="Generate {n} random integer numbers. {format_instructions}",
        input_values={"n": str(n)},
        temperature=0.0,
        output_parser=ListOfIntOutputParser(n),
    )


async def generate_with_env_var(n: int) -> list[int]:
    """Generate n random numbers using local model with environment variable."""
    # Set environment variable
    os.environ["LOCAL_MODEL_BASE_URL"] = "http://localhost:8000/v1"
    os.environ["LOCAL_MODEL_API_KEY"] = "your-api-key-if-needed"

    return await agenerate(
        model_name="local/meta-llama/Llama-3.2-1B",
        template="Generate {n} random integer numbers. {format_instructions}",
        input_values={"n": str(n)},
        temperature=0.0,
        output_parser=ListOfIntOutputParser(n),
    )


async def main() -> None:
    print("=" * 60)
    print("Example 1: Using local model with default configuration")
    print("=" * 60)
    print("Default URL: http://localhost:8000/v1")
    print()

    try:
        random_numbers = await asyncio.gather(
            *[generate_n_random_numbers_default(n) for n in range(2, 7)]
        )
        print(f"Generated random numbers: {random_numbers}")
    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure your local model server is running.")
        print("Example with vLLM:")
        print("  python -m vllm.entrypoints.openai.api_server --model meta-llama/Llama-3.2-1B --port 8000")

    print("\n" + "=" * 60)
    print("Example 2: Using local model with custom URL")
    print("=" * 60)
    try:
        result = await generate_with_custom_url(5)
        print(f"Generated numbers: {result}")
    except Exception as e:
        print(f"Error: {e}")

    print("\n" + "=" * 60)
    print("Example 3: Using local model with environment variables")
    print("=" * 60)
    try:
        result = await generate_with_env_var(5)
        print(f"Generated numbers: {result}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
