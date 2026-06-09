import time
from uuid import uuid4
from typing import Optional, Dict, List
import networkx as nx
from pyvis.network import Network
from pydantic import BaseModel

class MessageNode(BaseModel):
    node_id: str
    parent_id: Optional[str] = None
    root_id: str
    role: str  
    content: str
    timestamp: float
    depth: int

class SessionState(BaseModel):
    active_primary_goal: str
    current_root_id: str
    cognitive_state: str = "flow"  
    current_node_id: Optional[str] = None
    re_entry_primed: bool = False
    in_tangent: bool = False

class MemoryGraphManager:
    def __init__(self):
        self.G = nx.DiGraph()
        self.nodes_db: Dict[str, MessageNode] = {}
        
    def add_node(self, role: str, content: str, parent_id: Optional[str], root_id: str, depth: int) -> str:
        node_id = str(uuid4())
        node = MessageNode(
            node_id=node_id,
            parent_id=parent_id,
            root_id=root_id,
            role=role,
            content=content,
            timestamp=time.time(),
            depth=depth
        )
        self.nodes_db[node_id] = node
        self.G.add_node(node_id)
        if parent_id:
            self.G.add_edge(parent_id, node_id)
        return node_id

    def get_main_branch_history(self, target_node_id: str) -> List[MessageNode]:
        history = []
        current = target_node_id
        while current is not None:
            node = self.nodes_db.get(current)
            if not node:
                break
            history.insert(0, node)
            current = node.parent_id
        return history

    def generate_graph_html(self, current_root_id: str, filename="dag_visual.html"):
        net = Network(directed=True, height="600px", width="100%", bgcolor="#1a1a1a", font_color="white")
        net.toggle_physics(False)
        
        for node_id, node in self.nodes_db.items():
            if node_id == current_root_id:
                color = "#22c55e"  
            elif node.root_id == current_root_id:
                color = "#3b82f6"  
            else:
                color = "#f97316"  
                
            label = f"[{node.role.upper()}]\n" + (node.content[:25] + "..." if len(node.content) > 25 else node.content)
            hover_title = f"ID: {node_id}\nDepth: {node.depth}\nFull Content: {node.content}"
            net.add_node(node_id, label=label, title=hover_title, color=color, level=node.depth, shape="box")
            
        for u, v in self.G.edges():
            net.add_edge(u, v, color="#ffffff", width=1.5)
            
        net.set_options('{"layout": {"hierarchical": {"enabled": true, "direction": "UD", "sortMethod": "directed"}}}')
        net.write_html(filename)