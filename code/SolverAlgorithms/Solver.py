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

    # state: list các tuple của các xe, list của [{'A', 2, 3}, ...]
    # table: dict các (state, parent_state (để gen path), move, g(n), f(n)) 

    # input: init state: list những cái xe 
    # output: return list of moves [{'A', 0, 1},....]

    def __init__(self, map_obj):
        self.map = map_obj

    def get_state_key(self, vehicles):
        """Create a unique key for the current state"""
        return tuple((v.name, v.x, v.y) for v in vehicles)
    
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
                # Try moving left by 1 step
                new_x = vehicle.x - 1
                if self.is_valid_move_for_state(vehicles, i, new_x, vehicle.y):
                    moves.append({'name': vehicle.name, 'dx': -1, 'dy': 0, 'index': i})

                # Try moving right by 1 step
                new_x = vehicle.x + 1
                if self.is_valid_move_for_state(vehicles, i, new_x, vehicle.y):
                    moves.append({'name': vehicle.name, 'dx': 1, 'dy': 0, 'index': i})
            else:  # vertical
                # Try moving up by 1 step
                new_y = vehicle.y - 1
                if self.is_valid_move_for_state(vehicles, i, vehicle.x, new_y):
                    moves.append({'name': vehicle.name, 'dx': 0, 'dy': -1, 'index': i})

                # Try moving down by 1 step
                new_y = vehicle.y + 1
                if self.is_valid_move_for_state(vehicles, i, vehicle.x, new_y):
                    moves.append({'name': vehicle.name, 'dx': 0, 'dy': 1, 'index': i})
        
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
        vehicle_index = move['index']
        dx = move['dx']
        dy = move['dy']
        new_vehicles[vehicle_index].x += dx
        new_vehicles[vehicle_index].y += dy
        return new_vehicles

#==============================================
# Context: Puzzle Solver
#==============================================
class PuzzleSolver:
    def __init__(self, map_obj, strategy: SolverStrategy = None):
        self.map = map_obj
        self.strategy = strategy
    
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



