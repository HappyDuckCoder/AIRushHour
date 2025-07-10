from SolverAlgorithms.Solver import SolverStrategy, BaseSolver
import heapq
from typing import List, Dict, Tuple, Optional, Any

#==============================================
# Concrete Strategy: UCS with Vehicle Length Cost
#==============================================
class UCSStrategy(SolverStrategy, BaseSolver):
    """Uniform Cost Search strategy with vehicle length-based cost"""
    
    def __init__(self, map_obj):
        super().__init__(map_obj)
        self.table: Dict[str, Dict[str, Any]] = {}  
        self.solution: List[Dict[str, Any]] = []
        self.nodes_expanded = 0
        self.max_frontier_size = 0
    
    def get_name(self) -> str:
        return "UCS"
    
    def debug_vehicle_attributes(self, vehicle):
        """Debug method to inspect vehicle attributes"""
        if vehicle is None:
            print("[Debug] Vehicle is None")
            return
        
        print(f"[Debug] Vehicle attributes: {[attr for attr in dir(vehicle) if not attr.startswith('_')]}")
        
        # Print some common attributes if they exist
        for attr in ['name', 'x', 'y', 'length', 'size', 'width', 'height', 'positions', 'orientation']:
            if hasattr(vehicle, attr):
                value = getattr(vehicle, attr)
                print(f"[Debug] {attr}: {value}")
    
    def get_move_cost(self, vehicle) -> int:
        """Calculate cost based on vehicle length or size"""
        if vehicle is None:
            return 1  # Default cost for invalid vehicles
        
        # Try different possible attributes for vehicle size/length
        for attr in ['length', 'size', 'width', 'height']:
            if hasattr(vehicle, attr):
                value = getattr(vehicle, attr)
                if isinstance(value, (int, float)) and value > 0:
                    return int(value)
        
        # If vehicle has positions (method or property), calculate length from them
        if hasattr(vehicle, 'positions'):
            try:
                positions = vehicle.positions
                # Check if it's a method that needs to be called
                if callable(positions):
                    positions = positions()
                
                if positions and hasattr(positions, '__len__'):
                    return len(positions)
            except Exception as e:
                print(f"[Warning] Error getting positions: {e}")
        
        # Check if it's a horizontal or vertical vehicle and has start/end coordinates
        if hasattr(vehicle, 'x') and hasattr(vehicle, 'y'):
            if hasattr(vehicle, 'end_x') and hasattr(vehicle, 'end_y'):
                length = max(abs(vehicle.end_x - vehicle.x) + 1, abs(vehicle.end_y - vehicle.y) + 1)
                return length
        
        # Default cost if no size information is available
        print(f"[Warning] Could not determine vehicle size, using default cost of 2")
        return 2
    
    def find_vehicle_by_index(self, vehicles: List, vehicle_index: int):
        """Helper method to find vehicle by index"""
        if 0 <= vehicle_index < len(vehicles):
            return vehicles[vehicle_index]
        return None
    
    def ucs(self) -> bool:
        """UCS search for solution with vehicle length-based cost"""
        initial_vehicles = [v.copy() for v in self.map.vehicles]
        initial_state = self.get_state_key(initial_vehicles)
        
        # Priority queue: (cost, counter, state_key, vehicles, path)
        counter = 0
        frontier = [(0, counter, initial_state, initial_vehicles, [])]
        heapq.heapify(frontier)
        
        # Initialize tracking variables
        self.nodes_expanded = 0
        self.max_frontier_size = 0
        
        # Initialize table with initial state
        self.table[initial_state] = {
            'parent_state': None,
            'move': None,
            'g_n': 0,
            'f_n': 0,
            'visited': False
        }
        
        while frontier:
            # Track maximum frontier size for analysis
            self.max_frontier_size = max(self.max_frontier_size, len(frontier))
            
            current_cost, _, current_state_key, current_vehicles, current_path = heapq.heappop(frontier)
            
            # Skip if already visited (handles duplicate states)
            if self.table[current_state_key]['visited']:
                continue
            
            # Mark as visited and increment counter
            self.table[current_state_key]['visited'] = True
            self.nodes_expanded += 1
            
            # Check if goal state is reached
            if self.is_solved(current_vehicles):
                self.solution = current_path[:]
                return True
            
            # Generate possible moves
            moves = self.get_possible_moves(current_vehicles)
            
            for move in moves:
                # Validate move structure
                if not self._is_valid_move(move):
                    continue
                
                # Find the vehicle being moved
                vehicle_index = move.get('vehicle_index', move.get('index'))
                moved_vehicle = self.find_vehicle_by_index(current_vehicles, vehicle_index)
                
                if moved_vehicle is None:
                    print(f"[Warning] Vehicle with index {vehicle_index} not found or invalid")
                    continue
                
                # Debug: Print vehicle attributes (remove this after debugging)
                if self.nodes_expanded == 0:  # Only print once
                    self.debug_vehicle_attributes(moved_vehicle)
                
                # Calculate move cost and new state
                move_cost = self.get_move_cost(moved_vehicle)
                new_vehicles = self.apply_move(current_vehicles, move)
                new_state_key = self.get_state_key(new_vehicles)
                new_cost = current_cost + move_cost
                new_path = current_path + [move]
                
                # Add to frontier if not visited or if better path found
                if self._should_add_to_frontier(new_state_key, new_cost):
                    self.table[new_state_key] = {
                        'parent_state': current_state_key,
                        'move': move,
                        'g_n': new_cost,
                        'f_n': new_cost,
                        'visited': False
                    }
                    
                    counter += 1
                    heapq.heappush(frontier, (new_cost, counter, new_state_key, new_vehicles, new_path))
        
        return False
    
    def _is_valid_move(self, move: Dict[str, Any]) -> bool:
        """Validate move structure"""
        # Check for either 'vehicle_index' or 'index' key
        if 'vehicle_index' not in move and 'index' not in move:
            print(f"[Warning] Move missing vehicle identifier: {move}")
            return False
        return True
    
    def _should_add_to_frontier(self, state_key: str, cost: int) -> bool:
        """Determine if state should be added to frontier"""
        return (state_key not in self.table or 
                (not self.table[state_key]['visited'] and 
                 cost < self.table[state_key]['g_n']))
    
    def solve(self) -> Optional[List[Dict[str, Any]]]:
        """Solve the puzzle using UCS with vehicle length-based cost"""
        self.table.clear()  
        self.solution.clear()
        
        if self.ucs():
            return self.solution
        else:
            return None
    
    def get_solution_path(self) -> List[Dict[str, Any]]:
        """Get the solution path"""
        return self.solution[:] if self.solution else []
    
    def get_solution_cost(self) -> int:
        """Calculate total cost of solution"""
        if not self.solution:
            return 0
        
        total_cost = 0
        current_vehicles = [v.copy() for v in self.map.vehicles]
        
        for move in self.solution:
            if not self._is_valid_move(move):
                continue
            
            vehicle_index = move.get('vehicle_index', move.get('index'))
            moved_vehicle = self.find_vehicle_by_index(current_vehicles, vehicle_index)
            
            if moved_vehicle:
                total_cost += self.get_move_cost(moved_vehicle)
            
            current_vehicles = self.apply_move(current_vehicles, move)
        
        return total_cost
    
    def get_search_statistics(self) -> Dict[str, int]:
        """Get statistics about the search process"""
        return {
            'nodes_expanded': self.nodes_expanded,
            'max_frontier_size': self.max_frontier_size,
            'solution_length': len(self.solution),
            'solution_cost': self.get_solution_cost(),
            'states_explored': len([s for s in self.table.values() if s['visited']])
        }
    
    def reconstruct_path_from_table(self) -> List[Dict[str, Any]]:
        """Reconstruct path from table (alternative method)"""
        if not self.table:
            return []
        
        # Find goal state
        goal_state = self._find_goal_state()
        if not goal_state:
            return []
        
        # Reconstruct path backwards
        path = []
        current_state = goal_state
        
        while current_state and self.table[current_state]['parent_state']:
            move = self.table[current_state]['move']
            if move:
                path.append(move)
            current_state = self.table[current_state]['parent_state']
        
        path.reverse()
        return path
    
    def _find_goal_state(self) -> Optional[str]:
        """Find the goal state in the table"""
        for state_key, state_info in self.table.items():
            if state_info['visited']:
                try:
                    vehicles = self.state_key_to_vehicles(state_key)
                    if self.is_solved(vehicles):
                        return state_key
                except Exception as e:
                    print(f"[Warning] Error reconstructing vehicles from state: {e}")
                    continue
        return None
    
    def print_solution_details(self):
        """Print detailed solution information"""
        if not self.solution:
            print("No solution found")
            return
        
        print(f"\n=== UCS Solution Details ===")
        print(f"Solution found: Yes")
        print(f"Solution length: {len(self.solution)} moves")
        print(f"Total cost: {self.get_solution_cost()}")
        print(f"Nodes expanded: {self.nodes_expanded}")
        print(f"Max frontier size: {self.max_frontier_size}")
        
        print(f"\nSolution path:")
        for i, move in enumerate(self.solution, 1):
            print(f"  {i}. {move}")