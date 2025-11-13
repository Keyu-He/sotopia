# Example: Generate (2~7) random numbers using LM Studio models
# To run this example:
# 1. Download and install LM Studio from https://lmstudio.ai
# 2. Download a model in LM Studio (e.g., llama-3.2-1b)
# 3. Start the local server in LM Studio (default port: 1234)
# 4. Run this example:
#        uv run python examples/generation_api/lmstudio_model.py
#
# LM Studio models can be used in three ways:
# 1. Direct model name: "lmstudio/llama-3.2-1b" (uses default LM Studio port 1234)
# 2. With custom URL: "lmstudio/llama-3.2-1b@http://localhost:1234/v1"
# 3. With environment variable: Set LMSTUDIO_BASE_URL="http://localhost:1234/v1"
#
# Expected output: a bunch of logs and an output like [[14, 7], [14, 7, 3], [14, 7, 3, 9], [14, 7, 3, 9, 6], [14, 7, 3, 9, 6, 8]]

from sotopia.generation_utils import ListOfIntOutputParser, agenerate
import logging
import asyncio

# Set logging to the lowest level to show all logs
logging.basicConfig(level=0)


async def generate_n_random_numbers(n: int) -> list[int]:
    """Generate n random numbers using LM Studio."""
    return await agenerate(
        # Note: The model name in LM Studio might differ based on what you've loaded
        # Check the LM Studio local server page for the exact model name
        model_name="lmstudio/local-model",  # Default model name
        template="Generate {n} random integer numbers. {format_instructions}",
        input_values={"n": str(n)},
        temperature=0.0,
        output_parser=ListOfIntOutputParser(n),
    )


async def generate_with_custom_url(n: int) -> list[int]:
    """Generate n random numbers using LM Studio with custom URL."""
    return await agenerate(
        model_name="lmstudio/llama-3.2-1b@http://localhost:1234/v1",
        template="Generate {n} random integer numbers. {format_instructions}",
        input_values={"n": str(n)},
        temperature=0.0,
        output_parser=ListOfIntOutputParser(n),
    )


async def main() -> None:
    print("=" * 60)
    print("Example 1: Using LM Studio with default configuration")
    print("=" * 60)
    print("Note: Make sure LM Studio local server is running on port 1234")
    print("      and a model is loaded.")
    print()

    try:
        random_numbers = await asyncio.gather(
            *[generate_n_random_numbers(n) for n in range(2, 7)]
        )
        print(f"Generated random numbers: {random_numbers}")
    except Exception as e:
        print(f"Error: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure LM Studio is running")
        print("2. Check that a model is loaded in LM Studio")
        print("3. Verify the local server is started (check LM Studio's server tab)")
        print("4. The default URL is http://localhost:1234/v1")

    print("\n" + "=" * 60)
    print("Example 2: Using LM Studio with custom URL")
    print("=" * 60)
    try:
        result = await generate_with_custom_url(5)
        print(f"Generated numbers: {result}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
