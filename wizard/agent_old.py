from typing import Dict, Any, List
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from pydantic import BaseModel
import os

from .tools.crud import create_record, read_records, update_record, delete_record
from .tools.management import (
    describe_database, describe_table, create_table, alter_table,
    create_index, drop_index, manage_transaction
)
from .tools.utils import parse_sql_error

class WizardState(BaseModel):
    question: str
    messages: List[BaseMessage] = []
    current_step: str = "plan"
    tool_results: List[Dict[str, Any]] = []
    error_count: int = 0
    max_errors: int = 3
    final_answer: str = ""

class DatabaseWizard:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0,
            api_key=os.getenv("OPENAI_API_KEY")
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
            "manage_transaction": manage_transaction
        }
        
        self.system_prompt = """You are a Database LLM Wizard, a shamanic coder who bridges human intention with database reality.

Your sacred mission: Receive natural language requests and translate them into precise database operations using your 11 sacred tools.

CORE PRINCIPLES:
1. As Above, So Below: User intention (above) must manifest as database reality (below)
2. Universal Adapter: You work with ANY database, ANY schema - discover and create as needed
3. Agentic Reasoning: You can reflect, retry, and self-correct until the task is complete

YOUR 11 SACRED TOOLS:
Data Shaper (CRUD):
- create_record: Insert new data
- read_records: Query existing data  
- update_record: Modify existing data
- delete_record: Remove data

World Forger (Schema):
- describe_database: List all tables
- describe_table: Show table structure and row count
- create_table: Create new tables
- alter_table: Modify table structure

Grand Architect (Performance & Integrity):
- create_index: Add performance indexes
- drop_index: Remove indexes
- manage_transaction: Handle multi-step operations atomically

WORKFLOW:
1. Understand the user's intention
2. Determine what database operations are needed
3. Use describe_database/describe_table to understand current reality
4. Execute the required tools in logical order
5. If errors occur, analyze and retry with corrections
6. Return a natural language summary of what was accomplished

Remember: You are not bound by predetermined schemas. You discover, create, and adapt to whatever reality you encounter or need to manifest."""

        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        workflow = StateGraph(WizardState)
        
        workflow.add_node("plan", self._plan_node)
        workflow.add_node("execute", self._execute_node)
        workflow.add_node("reflect", self._reflect_node)
        workflow.add_node("finish", self._finish_node)
        
        workflow.set_entry_point("plan")
        
        workflow.add_conditional_edges(
            "plan",
            self._should_execute,
            {
                "execute": "execute",
                "finish": "finish"
            }
        )
        
        workflow.add_conditional_edges(
            "execute",
            self._should_continue,
            {
                "reflect": "reflect",
                "finish": "finish"
            }
        )
        
        workflow.add_conditional_edges(
            "reflect",
            self._should_retry,
            {
                "plan": "plan",
                "finish": "finish"
            }
        )
        
        workflow.add_edge("finish", END)
        
        return workflow.compile()

    async def _plan_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=f"Question: {state['question']}")
        ]
        
        if state.get('tool_results'):
            context = "\n".join([f"Previous result: {result}" for result in state['tool_results']])
            messages.append(HumanMessage(content=f"Context from previous actions:\n{context}"))
        
        response = await self.llm.ainvoke(messages)
        
        return {
            "messages": state.get("messages", []) + [response],
            "current_step": "execute"
        }

    async def _execute_node(self, state: WizardState) -> WizardState:
        # Extract tool call from the last AI message
        last_message = state.messages[-1]
        
        # Simple tool extraction (in production, use proper function calling)
        tool_name, tool_args = self._extract_tool_call(last_message.content)
        
        if tool_name and tool_name in self.tools:
            try:
                result = self.tools[tool_name](**tool_args)
                state.tool_results.append({
                    "tool": tool_name,
                    "args": tool_args,
                    "result": result,
                    "success": True
                })
                state.current_step = "reflect"
            except Exception as e:
                state.tool_results.append({
                    "tool": tool_name,
                    "args": tool_args,
                    "error": str(e),
                    "success": False
                })
                state.error_count += 1
                state.current_step = "reflect"
        else:
            state.current_step = "finish"
        
        return state

    async def _reflect_node(self, state: WizardState) -> WizardState:
        last_result = state.tool_results[-1] if state.tool_results else {}
        
        if last_result.get("success"):
            # Check if we need more actions
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=f"Original question: {state.question}"),
                HumanMessage(content=f"Last action result: {last_result}"),
                HumanMessage(content="Is the original question fully answered? If yes, provide a final answer. If no, what's the next action?")
            ]
        else:
            # Handle error and plan recovery
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=f"Original question: {state.question}"),
                HumanMessage(content=f"Error occurred: {last_result.get('error', 'Unknown error')}"),
                HumanMessage(content="How should we recover from this error? What's the corrected approach?")
            ]
        
        response = await self.llm.ainvoke(messages)
        state.messages.append(response)
        
        return state

    async def _finish_node(self, state: WizardState) -> WizardState:
        # Generate final answer based on all results
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=f"Original question: {state.question}"),
            HumanMessage(content=f"All results: {state.tool_results}"),
            HumanMessage(content="Provide a clear, natural language summary of what was accomplished.")
        ]
        
        response = await self.llm.ainvoke(messages)
        state.final_answer = response.content
        
        return state

    def _should_execute(self, state: WizardState) -> str:
        return "execute" if state.current_step == "execute" else "finish"

    def _should_continue(self, state: WizardState) -> str:
        return "reflect" if state.current_step == "reflect" else "finish"

    def _should_retry(self, state: WizardState) -> str:
        if state.error_count >= state.max_errors:
            return "finish"
        
        last_message = state.messages[-1].content.lower()
        if "next action" in last_message or "try again" in last_message:
            return "plan"
        else:
            return "finish"

    def _extract_tool_call(self, message_content: str) -> tuple:
        # Simplified tool extraction - in production, use proper function calling
        # This is a placeholder that needs to be implemented based on LLM response format
        return None, {}

    async def process(self, question: str) -> str:
        initial_state = WizardState(question=question)
        
        final_state = await self.graph.ainvoke(initial_state.model_dump())
        
        return final_state.get("final_answer", "I encountered difficulties processing your request.")
