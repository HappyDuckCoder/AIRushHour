from constants import *
from abc import ABC, abstractmethod

class SolverStrategy(ABC):
    
    @abstractmethod
    def solve(self, map_obj):
        pass
    
    @abstractmethod
    def get_name(self):
        pass

class BaseSolver:

    def __init__(self, map_obj):
        self.map = map_obj

    def get_state_key(self, vehicles):
        return tuple((v.name, v.x, v.y) for v in vehicles)
    
    def is_solved(self, vehicles):
        for vehicle in vehicles:
            if vehicle.name == 'A':
                rightmost_x = max(x for x, y in vehicle.positions())
                return rightmost_x == MAP_N - 1
        return False
    
    def get_possible_moves(self, vehicles):
        moves = []
        
        for i, vehicle in enumerate(vehicles):
            if vehicle.orient == 'h':
                new_x = vehicle.x - 1
                if self.is_valid_move_for_state(vehicles, i, new_x, vehicle.y):
                    moves.append({'name': vehicle.name, 'dx': -1, 'dy': 0, 'index': i})

                new_x = vehicle.x + 1
                if self.is_valid_move_for_state(vehicles, i, new_x, vehicle.y):
                    moves.append({'name': vehicle.name, 'dx': 1, 'dy': 0, 'index': i})
            else:
                new_y = vehicle.y - 1
                if self.is_valid_move_for_state(vehicles, i, vehicle.x, new_y):
                    moves.append({'name': vehicle.name, 'dx': 0, 'dy': -1, 'index': i})

                new_y = vehicle.y + 1
                if self.is_valid_move_for_state(vehicles, i, vehicle.x, new_y):
                    moves.append({'name': vehicle.name, 'dx': 0, 'dy': 1, 'index': i})
        
        return moves
    
    def is_valid_move_for_state(self, vehicles, vehicle_index, new_x, new_y):
        vehicle = vehicles[vehicle_index]

        test_positions = []
        if vehicle.orient == 'h':
            test_positions = [(new_x + i, new_y) for i in range(vehicle.len)]
        else:
            test_positions = [(new_x, new_y + i) for i in range(vehicle.len)]
        
        for x, y in test_positions:
            if not (0 <= x < MAP_N and 0 <= y < MAP_N):
                return False

        for j, other_vehicle in enumerate(vehicles):
            if j == vehicle_index:
                continue
            
            other_positions = set(other_vehicle.positions())
            if any(pos in other_positions for pos in test_positions):
                return False
        
        return True
    
    def apply_move(self, vehicles, move):
        new_vehicles = [v.copy() for v in vehicles]
        vehicle_index = move['index']
        dx = move['dx']
        dy = move['dy']
        new_vehicles[vehicle_index].x += dx
        new_vehicles[vehicle_index].y += dy
        return new_vehicles

class PuzzleSolver:
    def __init__(self, map_obj, strategy: SolverStrategy = None):
        self.map = map_obj
        self.strategy = strategy
    
    def set_strategy(self, strategy: SolverStrategy):
        self.strategy = strategy
    
    def solve(self):
        print(f"Using strategy: {self.strategy.get_name()}")
        return self.strategy.solve()
    
    def get_strategy_name(self):
        return self.strategy.get_name()