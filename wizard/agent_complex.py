import os
from typing import Any, TypedDict

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph

from .tools.crud import create_record, delete_record, read_records, update_record
from .tools.management import (
    alter_table,
    create_index,
    create_table,
    describe_database,
    describe_table,
    drop_index,
    manage_transaction,
)


class WizardState(TypedDict):
    question: str
    messages: list[BaseMessage]
    current_step: str
    tool_results: list[dict[str, Any]]
    error_count: int
    max_errors: int
    final_answer: str


class DatabaseWizard:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4", temperature=0, api_key=os.getenv("OPENAI_API_KEY")
        ).bind_tools(
            [
                {
                    "name": "create_record",
                    "description": "Insert new records into a table",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "table_name": {"type": "string"},
                            "data": {"type": "object"},
                        },
                        "required": ["table_name", "data"],
                    },
                },
                {
                    "name": "read_records",
                    "description": "Query records from a table",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "table_name": {"type": "string"},
                            "conditions": {"type": "object"},
                            "columns": {"type": "array", "items": {"type": "string"}},
                            "limit": {"type": "integer"},
                            "order_by": {"type": "string"},
                        },
                        "required": ["table_name"],
                    },
                },
                {
                    "name": "describe_database",
                    "description": "List all tables in the database",
                    "parameters": {"type": "object", "properties": {}},
                },
                {
                    "name": "describe_table",
                    "description": "Show table structure and row count",
                    "parameters": {
                        "type": "object",
                        "properties": {"table_name": {"type": "string"}},
                        "required": ["table_name"],
                    },
                },
                {
                    "name": "create_table",
                    "description": "Create a new table",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "table_name": {"type": "string"},
                            "columns": {"type": "array", "items": {"type": "object"}},
                            "constraints": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                        },
                        "required": ["table_name", "columns"],
                    },
                },
            ]
        )

        self.tools = {
            "create_record": create_record,
            "read_records": read_records,
            "update_record": update_record,
            "delete_record": delete_record,
            "describe_database": describe_database,
            "describe_table": describe_table,
            "create_table": create_table,
            "alter_table": alter_table,
            "create_index": create_index,
            "drop_index": drop_index,
            "manage_transaction": manage_transaction,
        }

        self.system_prompt = """You are a Database LLM Wizard, a shamanic coder who bridges human intention with database reality.

Your sacred mission: Receive natural language requests and translate them into precise database operations using your 11 sacred tools.

CORE PRINCIPLES:
1. As Above, So Below: User intention (above) must manifest as database reality (below)
2. Universal Adapter: You work with ANY database, ANY schema - discover and create as needed
3. Agentic Reasoning: You can reflect, retry, and self-correct until the task is complete

When you need to use a tool, respond with a tool call. The system will execute it and show you the results.

WORKFLOW:
1. Understand the user's intention
2. Determine what database operations are needed
3. Use describe_database/describe_table to understand current reality
4. Execute the required tools in logical order
5. If errors occur, analyze and retry with corrections
6. Return a natural language summary of what was accomplished"""

        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        workflow = StateGraph(WizardState)

        workflow.add_node("plan", self._plan_node)
        workflow.add_node("execute", self._execute_node)
        workflow.add_node("reflect", self._reflect_node)
        workflow.add_node("finish", self._finish_node)

        workflow.set_entry_point("plan")

        workflow.add_conditional_edges(
            "plan", self._should_execute, {"execute": "execute", "finish": "finish"}
        )

        workflow.add_conditional_edges(
            "execute", self._should_continue, {"reflect": "reflect", "finish": "finish"}
        )

        workflow.add_conditional_edges(
            "reflect", self._should_retry, {"plan": "plan", "finish": "finish"}
        )

        workflow.add_edge("finish", END)

        return workflow.compile()

    async def _plan_node(self, state: WizardState) -> dict[str, Any]:
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=f"Question: {state['question']}"),
        ]

        if state.get("tool_results"):
            context = "\n".join(
                [f"Previous result: {result}" for result in state["tool_results"]]
            )
            messages.append(
                HumanMessage(content=f"Context from previous actions:\n{context}")
            )

        response = await self.llm.ainvoke(messages)

        return {
            "messages": (state.get("messages") or []) + [response],
            "current_step": "execute",
        }

    async def _execute_node(self, state: WizardState) -> dict[str, Any]:
        messages = state.get("messages", [])
        if not messages:
            return {"current_step": "finish"}

        last_message = messages[-1]

        # Check if the message has tool calls
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            tool_call = last_message.tool_calls[0]
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]

            if tool_name in self.tools:
                try:
                    result = self.tools[tool_name](**tool_args)
                    tool_results = (state.get("tool_results") or []) + [
                        {
                            "tool": tool_name,
                            "args": tool_args,
                            "result": result,
                            "success": True,
                        }
                    ]
                    return {"tool_results": tool_results, "current_step": "reflect"}
                except Exception as e:
                    tool_results = (state.get("tool_results") or []) + [
                        {
                            "tool": tool_name,
                            "args": tool_args,
                            "error": str(e),
                            "success": False,
                        }
                    ]
                    return {
                        "tool_results": tool_results,
                        "error_count": state.get("error_count", 0) + 1,
                        "current_step": "reflect",
                    }

        return {"current_step": "finish"}

    async def _reflect_node(self, state: WizardState) -> dict[str, Any]:
        tool_results = state.get("tool_results", [])
        last_result = tool_results[-1] if tool_results else {}

        if last_result.get("success"):
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=f"Original question: {state['question']}"),
                HumanMessage(content=f"Last action result: {last_result}"),
                HumanMessage(
                    content="Is the original question fully answered? If yes, say 'DONE' and provide a final answer. If no, what's the next action?"
                ),
            ]
        else:
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=f"Original question: {state['question']}"),
                HumanMessage(
                    content=f"Error occurred: {last_result.get('error', 'Unknown error')}"
                ),
                HumanMessage(
                    content="How should we recover from this error? What's the corrected approach?"
                ),
            ]

        response = await self.llm.ainvoke(messages)

        return {"messages": (state.get("messages") or []) + [response]}

    async def _finish_node(self, state: WizardState) -> dict[str, Any]:
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=f"Original question: {state['question']}"),
            HumanMessage(content=f"All results: {state.get('tool_results', [])}"),
            HumanMessage(
                content="Provide a clear, natural language summary of what was accomplished."
            ),
        ]

        response = await self.llm.ainvoke(messages)

        return {"final_answer": response.content}

    def _should_execute(self, state: WizardState) -> str:
        return "execute" if state.get("current_step") == "execute" else "finish"

    def _should_continue(self, state: WizardState) -> str:
        return "reflect" if state.get("current_step") == "reflect" else "finish"

    def _should_retry(self, state: WizardState) -> str:
        if state.get("error_count", 0) >= state.get("max_errors", 3):
            return "finish"

        messages = state.get("messages", [])
        if messages and hasattr(messages[-1], "content"):
            last_message = messages[-1].content.lower()
            if "done" in last_message:
                return "finish"
            elif hasattr(messages[-1], "tool_calls") and messages[-1].tool_calls:
                return "plan"

        return "finish"

    async def process(self, question: str) -> str:
        initial_state = {
            "question": question,
            "messages": [],
            "current_step": "plan",
            "tool_results": [],
            "error_count": 0,
            "max_errors": 3,
            "final_answer": "",
        }

        final_state = await self.graph.ainvoke(initial_state, {"recursion_limit": 10})

        return final_state.get(
            "final_answer", "I encountered difficulties processing your request."
        )
