from constants import *

#== == == == == == == == == == == == == == == =
#DFS Solver
#== == == == == == == == == == == == == == == =
class DFSSolver:
    def __init__(self, map_obj):
        self.map = map_obj
        self.visited = set()
        self.solution = []
        
    def get_state_key(self, vehicles):
        """Create a unique key for the current state"""
        return tuple((v.x, v.y) for v in vehicles)
    
    def is_solved(self, vehicles):
        """Check if the puzzle is solved"""
        for vehicle in vehicles:
            if vehicle.is_target:
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
    
    def dfs(self, vehicles, path, depth=0, max_depth=50):
        """DFS search for solution"""
        if depth > max_depth:
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
            
            if self.dfs(new_vehicles, path, depth + 1, max_depth):
                return True
            
            path.pop()
        
        return False
    
    def solve(self):
        """Solve the puzzle and return list of moves"""
        self.visited.clear()
        self.solution.clear()
        
        initial_vehicles = [v.copy() for v in self.map.vehicles]
        
        if self.dfs(initial_vehicles, [], 0, 50):
            return self.solution
        else:
            return None