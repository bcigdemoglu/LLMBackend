import asyncio

from wizard.agent import DatabaseWizard


async def test_graph():
    wizard = DatabaseWizard()

    # Enable debug mode
    import os

    os.environ["LANGCHAIN_VERBOSE"] = "true"

    try:
        result = await wizard.process("What tables exist?")
        print(f"Result: {result}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()


asyncio.run(test_graph())
