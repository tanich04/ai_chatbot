import os
import dateparser
from datetime import datetime
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode
from langchain_groq import ChatGroq
from langchain_core.tools import tool
from typing import Literal
from langchain_core.messages import HumanMessage
from mock_calendar import (
    check_availability, create_event, delete_event, modify_event,
    get_calendar_day_view, get_calendar_week_view
)

@tool
def check_slot(date: str) -> str:
    """Check available slots for a given date."""
    return check_availability(date)

@tool
def book_slot(date: str, time: str, title: str) -> str:
    """Book a slot on a given date and time."""
    try:
        time = datetime.strptime(time, "%H:%M:%S").strftime("%I:%M %p")
    except:
        pass
    return create_event(date, time, title)

@tool
def delete_slot(date: str, time: str) -> str:
    """Delete a scheduled meeting."""
    return delete_event(date, time)

@tool
def modify_slot(date: str, old_time: str, new_time: str) -> str:
    """Move a meeting to a different time."""
    return modify_event(date, old_time, new_time)

@tool
def view_day(date: str) -> str:
    """View events on a specific day."""
    return get_calendar_day_view(date)

@tool
def view_week(date: str) -> str:
    """View events during a week starting from a date."""
    return get_calendar_week_view(date)

class BookingBot:
    def __init__(self):
        self.llm = ChatGroq(api_key=os.getenv("GROQ_API_KEY"), model_name="llama3-8b-8192")
        self.tools = [check_slot, book_slot, delete_slot, modify_slot, view_day, view_week]
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        self.tool_node = ToolNode(tools=self.tools)

    def call_model(self, state: MessagesState):
        messages = state["messages"]
        response = self.llm_with_tools.invoke(messages)
        print("🧠 Bot:", response.content)
        print("🔧 Tool Calls:", response.tool_calls)
        return {"messages": [response]}

    def router(self, state: MessagesState) -> Literal["tools", END]:
        messages = state["messages"]
        if messages[-1].tool_calls:
            return "tools"
        return END

    def build(self):
        graph = StateGraph(MessagesState)
        graph.add_node("agent", self.call_model)
        graph.add_node("tools", self.tool_node)
        graph.add_edge(START, "agent")
        graph.add_conditional_edges("agent", self.router, {"tools": "tools", END: END})
        graph.add_edge("tools", "agent")
        return graph.compile()

def build_bot():
    return BookingBot().build()
