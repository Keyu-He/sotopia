# Example: Generate (2~7) random numbers using Ollama models
# To run this example:
# 1. Install Ollama from https://ollama.ai
# 2. Pull a model: ollama pull llama3.2:1b
# 3. Run this example:
#        uv run python examples/generation_api/ollama_model.py
#
# Ollama models can be used in three ways:
# 1. Direct model name: "ollama/llama3.2:1b" (uses default Ollama port 11434)
# 2. With custom URL: "ollama/llama3.2:1b@http://localhost:11434"
# 3. With environment variable: Set OLLAMA_BASE_URL="http://localhost:11434"
#
# Expected output: a bunch of logs and an output like [[14, 7], [14, 7, 3], [14, 7, 3, 9], [14, 7, 3, 9, 6], [14, 7, 3, 9, 6, 8]]

from sotopia.generation_utils import ListOfIntOutputParser, agenerate
import logging
import asyncio

# Set logging to the lowest level to show all logs
logging.basicConfig(level=0)


async def generate_n_random_numbers(n: int) -> list[int]:
    """Generate n random numbers using Ollama."""
    return await agenerate(
        model_name="ollama/llama3.2:1b",  # Uses LiteLLM's native Ollama support
        template="Generate {n} random integer numbers. {format_instructions}",
        input_values={"n": str(n)},
        temperature=0.0,
        output_parser=ListOfIntOutputParser(n),
    )


async def generate_with_custom_url(n: int) -> list[int]:
    """Generate n random numbers using Ollama with custom URL."""
    return await agenerate(
        model_name="ollama/llama3.2:1b@http://localhost:11434",
        template="Generate {n} random integer numbers. {format_instructions}",
        input_values={"n": str(n)},
        temperature=0.0,
        output_parser=ListOfIntOutputParser(n),
    )


async def main() -> None:
    print("=" * 60)
    print("Example 1: Using Ollama with default configuration")
    print("=" * 60)
    try:
        random_numbers = await asyncio.gather(
            *[generate_n_random_numbers(n) for n in range(2, 7)]
        )
        print(f"Generated random numbers: {random_numbers}")
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure Ollama is running and the model is pulled:")
        print("  ollama pull llama3.2:1b")
        print("  ollama serve")

    print("\n" + "=" * 60)
    print("Example 2: Using Ollama with custom URL")
    print("=" * 60)
    try:
        result = await generate_with_custom_url(5)
        print(f"Generated numbers: {result}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
