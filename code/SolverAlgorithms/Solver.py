from constants import *
from abc import ABC, abstractmethod

#==============================================
# Strategy Interface
#==============================================
class SolverStrategy(ABC):
    """Abstract base class for solving strategies"""
    
    @abstractmethod
    def solve(self, map_obj):
        """Solve the puzzle and return list of moves"""
        pass
    
    @abstractmethod
    def get_name(self):
        """Return the name of the strategy"""
        pass

#==============================================
# Base Solver Class (Common functionality)
#==============================================
class BaseSolver:

    # state: list các tuple của các xe 
    # table: dict các (state, parent_state (để gen path), move, g(n), f(n)) 

    def __init__(self, map_obj):
        self.map = map_obj

    def get_state_key(self, vehicles):
        """Create a unique key for the current state"""
        return tuple((v.x, v.y) for v in vehicles)
    
    def is_solved(self, vehicles):
        """Check if the puzzle is solved"""
        for vehicle in vehicles:
            if vehicle.name == 'A':
                rightmost_x = max(x for x, y in vehicle.positions())
                return rightmost_x == MAP_N - 1
        return False
    
    def get_possible_moves(self, vehicles):
        """Get all possible moves for current state"""
        moves = []
        
        for i, vehicle in enumerate(vehicles):
            if vehicle.orient == 'h':
                #Try moving left
                for new_x in range(vehicle.x - 1, -1, -1):
                    if self.is_valid_move_for_state(vehicles, i, new_x, vehicle.y):
                        moves.append((i, new_x - vehicle.x, 0))
                    else:
                        break

                #Try moving right
                for new_x in range(vehicle.x + 1, MAP_N):
                    if self.is_valid_move_for_state(vehicles, i, new_x, vehicle.y):
                        moves.append((i, new_x - vehicle.x, 0))
                    else:
                        break
            else:  # vertical
                #Try moving up
                for new_y in range(vehicle.y - 1, -1, -1):
                    if self.is_valid_move_for_state(vehicles, i, vehicle.x, new_y):
                        moves.append((i, 0, new_y - vehicle.y))
                    else:
                        break

                #Try moving down
                for new_y in range(vehicle.y + 1, MAP_N):
                    if self.is_valid_move_for_state(vehicles, i, vehicle.x, new_y):
                        moves.append((i, 0, new_y - vehicle.y))
                    else:
                        break
        
        return moves
    
    def is_valid_move_for_state(self, vehicles, vehicle_index, new_x, new_y):
        """Check if a move is valid for given state"""
        vehicle = vehicles[vehicle_index]

        #Check bounds
        test_positions = []
        if vehicle.orient == 'h':
            test_positions = [(new_x + i, new_y) for i in range(vehicle.len)]
        else:
            test_positions = [(new_x, new_y + i) for i in range(vehicle.len)]
        
        for x, y in test_positions:
            if not (0 <= x < MAP_N and 0 <= y < MAP_N):
                return False

        #Check collisions with other vehicles
        for j, other_vehicle in enumerate(vehicles):
            if j == vehicle_index:
                continue
            
            other_positions = set(other_vehicle.positions())
            if any(pos in other_positions for pos in test_positions):
                return False
        
        return True
    
    def apply_move(self, vehicles, move):
        """Apply a move to the vehicles and return new state"""
        new_vehicles = [v.copy() for v in vehicles]
        vehicle_index, dx, dy = move
        new_vehicles[vehicle_index].x += dx
        new_vehicles[vehicle_index].y += dy
        return new_vehicles

    # def encode_state(state_tuple):

    # def decode_state(state_bytes):

    # def encode_table_entry():

    # def decode_table_entry():

    # def build_board_2d():

    # def compute_blocked_map():

    # precompute_helpful_moves():

    # relative_helful_move():

    # generate_successors():

    # reconstruct_path():

    # is_solved:

#==============================================
# Concrete Strategy: DFS
#==============================================
class DFSStrategy(SolverStrategy, BaseSolver):
    """Depth-First Search strategy"""
    
    def __init__(self, map_obj, max_depth=50):
        super().__init__(map_obj)
        self.max_depth = max_depth
        self.visited = set()
        self.solution = []
    
    def get_name(self):
        return f"DFS (max_depth={self.max_depth})"
    
    def dfs(self, vehicles, path, depth=0):
        """DFS search for solution"""
        if depth > self.max_depth:
            return False
            
        state_key = self.get_state_key(vehicles)
        if state_key in self.visited:
            return False
        
        self.visited.add(state_key)
        
        if self.is_solved(vehicles):
            self.solution = path[:]
            return True
        
        moves = self.get_possible_moves(vehicles)
        
        for move in moves:
            new_vehicles = self.apply_move(vehicles, move)
            path.append(move)
            
            if self.dfs(new_vehicles, path, depth + 1):
                return True
            
            path.pop()
        
        return False
    
    def solve(self):
        """Solve the puzzle using DFS"""
        self.visited.clear()
        self.solution.clear()
        
        initial_vehicles = [v.copy() for v in self.map.vehicles]
        
        if self.dfs(initial_vehicles, [], 0):
            return self.solution
        else:
            return None

#==============================================
# Concrete Strategy: BFS
#==============================================
from collections import deque

class BFSStrategy(SolverStrategy, BaseSolver):
    """Breadth-First Search strategy"""
    
    def __init__(self, map_obj, max_moves=1000):
        super().__init__(map_obj)
        self.max_moves = max_moves
    
    def get_name(self):
        return f"BFS (max_moves={self.max_moves})"
    
    def solve(self):
        """Solve the puzzle using BFS"""
        initial_vehicles = [v.copy() for v in self.map.vehicles]
        initial_state = self.get_state_key(initial_vehicles)
        
        if self.is_solved(initial_vehicles):
            return []
        
        queue = deque([(initial_vehicles, [])])
        visited = {initial_state}
        moves_count = 0
        
        while queue and moves_count < self.max_moves:
            current_vehicles, path = queue.popleft()
            moves_count += 1
            
            moves = self.get_possible_moves(current_vehicles)
            
            for move in moves:
                new_vehicles = self.apply_move(current_vehicles, move)
                new_state = self.get_state_key(new_vehicles)
                
                if new_state not in visited:
                    visited.add(new_state)
                    new_path = path + [move]
                    
                    if self.is_solved(new_vehicles):
                        return new_path
                    
                    queue.append((new_vehicles, new_path))
        
        return None


#==============================================
# Concrete Strategy: UCS
#==============================================
class UCSStrategy(SolverStrategy, BaseSolver):
    """Uniform Cost Search strategy"""
    pass

#==============================================
# Context: Puzzle Solver
#==============================================
class PuzzleSolver:
    def __init__(self, map_obj, strategy: SolverStrategy = None):
        self.map = map_obj
        self.strategy = strategy or DFSStrategy(map_obj)
    
    def set_strategy(self, strategy: SolverStrategy):
        """Change the solving strategy"""
        self.strategy = strategy
    
    def solve(self):
        """Solve the puzzle using current strategy"""
        print(f"Using strategy: {self.strategy.get_name()}")
        return self.strategy.solve()
    
    def get_strategy_name(self):
        """Get the name of current strategy"""
        return self.strategy.get_name()

#==============================================
# Strategy Factory (Optional - for easy creation)
#==============================================
class StrategyFactory:
    """Factory to create different strategies"""
    
    @staticmethod
    def create_dfs(map_obj, max_depth=50):
        return DFSStrategy(map_obj, max_depth)
    
    @staticmethod
    def create_bfs(map_obj, max_moves=1000):
        return BFSStrategy(map_obj, max_moves)
