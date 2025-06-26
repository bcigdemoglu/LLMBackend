import asyncio

from wizard.agent import DatabaseWizard


async def test_direct():
    wizard = DatabaseWizard()

    # Test graph nodes directly
    initial_state = {
        "question": "What tables exist?",
        "messages": [],
        "current_step": "plan",
        "tool_results": [],
        "error_count": 0,
        "max_errors": 3,
        "final_answer": "",
    }

    print("Testing plan node...")
    plan_result = await wizard._plan_node(initial_state)
    print(f"Plan result: {plan_result}")

    # Update state
    for k, v in plan_result.items():
        if v is not None:
            initial_state[k] = v

    print(f"\nCurrent step after plan: {initial_state.get('current_step')}")
    print(f"Messages: {len(initial_state.get('messages', []))}")

    if initial_state.get("messages"):
        msg = initial_state["messages"][-1]
        print(f"Last message type: {type(msg)}")
        print(f"Has tool_calls: {hasattr(msg, 'tool_calls')}")
        if hasattr(msg, "tool_calls"):
            print(f"Tool calls: {msg.tool_calls}")


asyncio.run(test_direct())
