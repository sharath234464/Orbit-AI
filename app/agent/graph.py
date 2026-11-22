from langgraph.graph import END, START, StateGraph
from app.agent.state import RoutingState
from app.agent.nodes import classify_task_node, make_select_provider_node

def build_routing_graph(settings, providers: dict):
    graph = StateGraph(RoutingState)
    graph.add_node("classify_task", classify_task_node)
    graph.add_node("select_provider", make_select_provider_node(settings, providers))
    graph.add_edge(START, "classify_task")
    graph.add_edge("classify_task", "select_provider")
    graph.add_edge("select_provider", END)
    return graph.compile()
