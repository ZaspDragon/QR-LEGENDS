
import json
import math
import heapq
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Node:
    id: str
    x: float
    y: float
    z: float = 0.0

@dataclass 
class Edge:
    from_node: str
    to_node: str
    cost: float = 1.0

class WarehouseNavigator:
    """A* pathfinding for warehouse navigation"""
    
    def __init__(self):
        self.nodes: Dict[str, Node] = {}
        self.edges: Dict[str, List[Edge]] = {}
        self.congestion: Dict[str, float] = {}
        
    def add_node(self, node_id: str, x: float, y: float, z: float = 0.0):
        """Add a navigation node"""
        self.nodes[node_id] = Node(node_id, x, y, z)
        if node_id not in self.edges:
            self.edges[node_id] = []
    
    def add_edge(self, from_node: str, to_node: str, cost: float = 1.0):
        """Add a bidirectional edge between nodes"""
        if from_node not in self.edges:
            self.edges[from_node] = []
        if to_node not in self.edges:
            self.edges[to_node] = []
            
        self.edges[from_node].append(Edge(from_node, to_node, cost))
        self.edges[to_node].append(Edge(to_node, from_node, cost))
    
    def set_congestion(self, from_node: str, to_node: str, multiplier: float):
        """Set congestion multiplier for a specific edge"""
        edge_key = f"{from_node}->{to_node}"
        self.congestion[edge_key] = multiplier
    
    def heuristic(self, node_a: str, node_b: str) -> float:
        """Calculate heuristic distance between nodes"""
        if node_a not in self.nodes or node_b not in self.nodes:
            return float('inf')
        
        a = self.nodes[node_a]
        b = self.nodes[node_b]
        
        # Euclidean distance
        dx = a.x - b.x
        dy = a.y - b.y
        dz = a.z - b.z
        
        return math.sqrt(dx*dx + dy*dy + dz*dz)
    
    def get_edge_cost(self, from_node: str, to_node: str, base_cost: float) -> float:
        """Get actual edge cost including congestion"""
        edge_key = f"{from_node}->{to_node}"
        multiplier = self.congestion.get(edge_key, 1.0)
        return base_cost * multiplier
    
    def find_path(self, start: str, goal: str) -> Optional[Dict]:
        """Find shortest path using A* algorithm"""
        if start not in self.nodes or goal not in self.nodes:
            return None
        
        # A* algorithm implementation
        open_set = [(0, start)]
        came_from = {}
        g_score = {start: 0}
        f_score = {start: self.heuristic(start, goal)}
        
        while open_set:
            current_f, current = heapq.heappop(open_set)
            
            if current == goal:
                # Reconstruct path
                path = [current]
                while current in came_from:
                    current = came_from[current]
                    path.append(current)
                path.reverse()
                
                # Generate turn-by-turn directions
                directions = self.generate_directions(path)
                
                return {
                    'path': path,
                    'cost': g_score[goal],
                    'directions': directions,
                    'distance_meters': g_score[goal],
                    'estimated_time_minutes': g_score[goal] / 1.4  # Assume 1.4 m/s walking speed
                }
            
            # Check neighbors
            for edge in self.edges.get(current, []):
                neighbor = edge.to_node
                tentative_g = g_score[current] + self.get_edge_cost(current, neighbor, edge.cost)
                
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + self.heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
        
        return None  # No path found
    
    def generate_directions(self, path: List[str]) -> List[Dict]:
        """Generate turn-by-turn directions from path"""
        if len(path) < 2:
            return []
        
        directions = []
        
        for i in range(len(path)):
            node = self.nodes[path[i]]
            
            if i == 0:
                directions.append({
                    'step': i + 1,
                    'instruction': f"Start at {path[i]}",
                    'location': path[i],
                    'coordinates': {'x': node.x, 'y': node.y, 'z': node.z},
                    'type': 'start'
                })
            elif i == len(path) - 1:
                directions.append({
                    'step': i + 1,
                    'instruction': f"Arrive at {path[i]}",
                    'location': path[i],
                    'coordinates': {'x': node.x, 'y': node.y, 'z': node.z},
                    'type': 'destination'
                })
            else:
                # Determine direction
                prev_node = self.nodes[path[i-1]]
                curr_node = self.nodes[path[i]]
                
                dx = curr_node.x - prev_node.x
                dz = curr_node.z - prev_node.z
                
                direction = "forward"
                if abs(dx) > abs(dz):
                    direction = "east" if dx > 0 else "west"
                else:
                    direction = "south" if dz > 0 else "north"
                
                directions.append({
                    'step': i + 1,
                    'instruction': f"Head {direction} to {path[i]}",
                    'location': path[i],
                    'coordinates': {'x': node.x, 'y': node.y, 'z': node.z},
                    'type': 'waypoint',
                    'direction': direction
                })
        
        return directions
    
    def load_warehouse_graph(self, graph_data: Dict):
        """Load warehouse graph from JSON data"""
        # Clear existing data
        self.nodes.clear()
        self.edges.clear()
        
        # Load nodes
        for node_data in graph_data.get('nodes', []):
            self.add_node(
                node_data['id'],
                node_data['x'],
                node_data['y'],
                node_data.get('z', 0.0)
            )
        
        # Load edges
        for edge_data in graph_data.get('edges', []):
            self.add_edge(
                edge_data['from'],
                edge_data['to'],
                edge_data.get('cost', 1.0)
            )
    
    def get_nearby_locations(self, location: str, radius: float = 10.0) -> List[str]:
        """Get locations within radius of given location"""
        if location not in self.nodes:
            return []
        
        center = self.nodes[location]
        nearby = []
        
        for node_id, node in self.nodes.items():
            if node_id == location:
                continue
            
            distance = math.sqrt(
                (node.x - center.x)**2 + 
                (node.y - center.y)**2 + 
                (node.z - center.z)**2
            )
            
            if distance <= radius:
                nearby.append(node_id)
        
        return nearby

# Create sample warehouse graph
def create_sample_warehouse_graph():
    """Create a sample warehouse graph for demo purposes"""
    nav = WarehouseNavigator()
    
    # Add nodes in a grid pattern
    zones = ['A', 'B', 'C']
    for zone_idx, zone in enumerate(zones):
        y_offset = zone_idx * 60.0
        
        # Corridor spine
        for bay in range(11):
            node_id = f"{zone}-00-{bay:02d}"
            nav.add_node(node_id, bay * 5.0, 0, y_offset)
            
            if bay > 0:
                prev_id = f"{zone}-00-{bay-1:02d}"
                nav.add_edge(prev_id, node_id, 1.0)
        
        # Aisles
        for aisle in range(1, 5):
            for bay in range(11):
                node_id = f"{zone}-{aisle:02d}-{bay:02d}"
                nav.add_node(node_id, bay * 5.0, 0, y_offset + aisle * 10.0)
                
                # Connect along aisle
                if bay > 0:
                    prev_id = f"{zone}-{aisle:02d}-{bay-1:02d}"
                    nav.add_edge(prev_id, node_id, 1.0)
                
                # Connect to corridor
                corridor_id = f"{zone}-00-{bay:02d}"
                nav.add_edge(corridor_id, node_id, 1.0)
    
    return nav

# Global navigator instance
warehouse_navigator = create_sample_warehouse_graph()
