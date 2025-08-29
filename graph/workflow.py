# orchestration/workflow.py
from typing import Dict, Any
from langgraph.graph import StateGraph, END

from .nodes import (
    node_perceive, node_execute, node_evaluate,
    node_recover, node_finish, decide_next
)

def build_workflow():
    g = StateGraph(dict)
    g.add_node("perceive", node_perceive)
    g.add_node("execute", node_execute)
    g.add_node("evaluate", node_evaluate)
    g.add_node("recover", node_recover)
    g.add_node("finish", node_finish)

    g.set_entry_point("perceive")
    g.add_edge("perceive", "execute")
    g.add_edge("execute", "evaluate")
    g.add_conditional_edges("evaluate", decide_next, {
        "recover": "recover",
        "finish": "finish",
    })
    g.add_edge("recover", "perceive")
    return g.compile()
