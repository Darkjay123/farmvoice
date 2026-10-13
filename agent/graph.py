"""LangGraph orchestration with a human-in-the-loop approval gate (interrupt)."""
from langgraph.graph import StateGraph, END

def plan(state):
    # Decompose the officer's request into tool calls
    return {"plan": ["get_rainfall", "get_prices", "get_plot_history", "draft_advisory"]}

def gather(state):
    return {"gathered": True}

def approval_gate(state):
    """Interrupt node: a named human officer must approve before the advisory is sent."""
    if not state.get("officer_approval"):
        raise Interrupt("officer_approval required before sending")

def send(state):
    return {"sent": True}

class Interrupt(Exception):
    pass

def build():
    g = StateGraph(dict)
    g.add_node("plan", plan)
    g.add_node("gather", gather)
    g.add_node("approval_gate", approval_gate)
    g.add_node("send", send)
    g.set_entry_point("plan")
    g.add_edge("plan", "gather")
    g.add_edge("gather", "approval_gate")
    g.add_edge("approval_gate", "send")
    g.add_edge("send", END)
    return g.compile()
