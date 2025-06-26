from typing import Dict, Any, List, TypedDict, Annotated, Sequence
from langgraph.graph import StateGraph, END, add_messages
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage, ToolMessage
import os
import json
from datetime import datetime

from .tools.crud import create_record, read_records, update_record, delete_record
from .tools.management import (
    describe_database, describe_table, create_table, alter_table,
    create_index, drop_index, manage_transaction
)

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

class DatabaseWizard:
    def __init__(self):
        self.current_log_file = None
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
        
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            api_key=os.getenv("OPENAI_API_KEY")
        ).bind_tools([
            {
                "name": "describe_database",
                "description": "List all tables in the database",
                "parameters": {"type": "object", "properties": {}}
            },
            {
                "name": "describe_table",
                "description": "Show table structure and row count",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "table_name": {"type": "string"}
                    },
                    "required": ["table_name"]
                }
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
                        "order_by": {"type": "string"}
                    },
                    "required": ["table_name"]
                }
            },
            {
                "name": "create_record",
                "description": "Insert new records into a table",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "table_name": {"type": "string"},
                        "data": {"type": "object"}
                    },
                    "required": ["table_name", "data"]
                }
            },
            {
                "name": "create_table",
                "description": "Create a new table",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "table_name": {"type": "string"},
                        "columns": {"type": "array", "items": {"type": "object"}},
                        "constraints": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["table_name", "columns"]
                }
            }
        ])
        
        self.system_message = SystemMessage(content="""You are a Database LLM Wizard. Your job is to:
1. Understand natural language database queries
2. Use the provided tools to interact with the database
3. Return clear, natural language responses

Always start by understanding what exists in the database before making changes.""")
        
        self.graph = self._build_graph()
    
    def _log_llm_interaction(self, messages: List[BaseMessage], response: AIMessage):
        """Log LLM interactions to file"""
        if not self.current_log_file:
            return
            
        try:
            with open(self.current_log_file, 'a') as f:
                timestamp = datetime.now().isoformat()
                
                # Log input
                f.write(f"\n{'='*80}\n")
                f.write(f"Timestamp: {timestamp}\n")
                f.write(f"Direction: INPUT\n")
                f.write(f"Messages:\n")
                for msg in messages:
                    msg_type = type(msg).__name__
                    content = msg.content
                    f.write(f"  - {msg_type}: {content}\n")
                    if hasattr(msg, 'tool_calls') and msg.tool_calls:
                        f.write(f"    Tool Calls: {msg.tool_calls}\n")
                
                # Log output
                f.write(f"\nDirection: OUTPUT\n")
                f.write(f"Response: {response.content}\n")
                if hasattr(response, 'tool_calls') and response.tool_calls:
                    f.write(f"Tool Calls: {response.tool_calls}\n")
                
                # Log token usage if available
                if hasattr(response, 'usage_metadata') and response.usage_metadata:
                    f.write(f"\nToken Usage:\n")
                    f.write(f"  - Input Tokens: {response.usage_metadata.get('input_tokens', 'N/A')}\n")
                    f.write(f"  - Output Tokens: {response.usage_metadata.get('output_tokens', 'N/A')}\n")
                    f.write(f"  - Total Tokens: {response.usage_metadata.get('total_tokens', 'N/A')}\n")
                elif hasattr(response, 'response_metadata') and response.response_metadata:
                    token_usage = response.response_metadata.get('token_usage', {})
                    if token_usage:
                        f.write(f"\nToken Usage:\n")
                        f.write(f"  - Input Tokens: {token_usage.get('prompt_tokens', 'N/A')}\n")
                        f.write(f"  - Output Tokens: {token_usage.get('completion_tokens', 'N/A')}\n")
                        f.write(f"  - Total Tokens: {token_usage.get('total_tokens', 'N/A')}\n")
                
                f.write(f"{'='*80}\n")
                
        except Exception as e:
            print(f"Error logging LLM interaction: {e}")
    
    def _build_graph(self) -> StateGraph:
        workflow = StateGraph(AgentState)
        
        workflow.add_node("agent", self._call_model)
        workflow.add_node("tools", self._call_tools)
        
        workflow.set_entry_point("agent")
        
        workflow.add_conditional_edges(
            "agent",
            self._should_continue,
            {
                "continue": "tools",
                "end": END
            }
        )
        
        workflow.add_edge("tools", "agent")
        
        return workflow.compile()
    
    def _should_continue(self, state: AgentState):
        messages = state["messages"]
        last_message = messages[-1]
        
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "continue"
        
        return "end"
    
    async def _call_model(self, state: AgentState):
        messages = state["messages"]
        response = await self.llm.ainvoke(messages)
        
        # Log the interaction
        self._log_llm_interaction(messages, response)
        
        return {"messages": [response]}
    
    async def _call_tools(self, state: AgentState):
        messages = state["messages"]
        last_message = messages[-1]
        
        tool_messages = []
        for tool_call in last_message.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            
            if tool_name in self.tools:
                try:
                    result = self.tools[tool_name](**tool_args)
                    tool_messages.append(
                        ToolMessage(
                            content=json.dumps(result),
                            tool_call_id=tool_call["id"]
                        )
                    )
                except Exception as e:
                    tool_messages.append(
                        ToolMessage(
                            content=f"Error: {str(e)}",
                            tool_call_id=tool_call["id"]
                        )
                    )
            else:
                tool_messages.append(
                    ToolMessage(
                        content=f"Tool {tool_name} not found",
                        tool_call_id=tool_call["id"]
                    )
                )
        
        return {"messages": tool_messages}
    
    async def process(self, question: str) -> str:
        # Create logs directory if it doesn't exist
        logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
        os.makedirs(logs_dir, exist_ok=True)
        
        # Create log file for this request
        timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        self.current_log_file = os.path.join(logs_dir, f"ask-{timestamp}.log")
        
        # Log the initial question
        with open(self.current_log_file, 'w') as f:
            f.write(f"Question: {question}\n")
            f.write(f"Timestamp: {datetime.now().isoformat()}\n")
            f.write(f"Model: gpt-4o-mini\n")
            f.write("="*80 + "\n")
        
        initial_state = {
            "messages": [
                self.system_message,
                HumanMessage(content=question)
            ]
        }
        
        try:
            final_state = await self.graph.ainvoke(
                initial_state,
                {"recursion_limit": 15}
            )
            
            # Get the final response
            last_message = final_state["messages"][-1]
            if hasattr(last_message, "content"):
                result = last_message.content
            else:
                result = "I processed your request successfully."
            
            # Log the final result
            with open(self.current_log_file, 'a') as f:
                f.write(f"\n{'='*80}\n")
                f.write(f"FINAL ANSWER:\n{result}\n")
                f.write(f"Completed at: {datetime.now().isoformat()}\n")
            
            return result
                
        except Exception as e:
            error_msg = f"I encountered an error: {str(e)}"
            
            # Log the error
            with open(self.current_log_file, 'a') as f:
                f.write(f"\n{'='*80}\n")
                f.write(f"ERROR: {str(e)}\n")
                f.write(f"Error at: {datetime.now().isoformat()}\n")
            
            return error_msg