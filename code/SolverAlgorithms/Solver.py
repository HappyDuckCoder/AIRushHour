from constants import *
from abc import ABC, abstractmethod
import heapdict
import time
from collections import defaultdict
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
    PADDING = bytes([150]) 

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
    def encode_state(self, state_tuple):
        # Encode a sorted state tuple into bytes.
        state = tuple(sorted(state_tuple))
        return b''.join(bytes([ord(name), x, y]) for name, x, y in state)
    
    # def decode_state(state_bytes):
    def decode_state(self, state_bytes):
        # Decode bytes back into a list of (name, x, y) tuples.
        return [(chr(state_bytes[i]), state_bytes[i+1], state_bytes[i+2]) for i in range(0, len(state_bytes), 3)]
    
    def encode_signed(self, val):
        return val % 256

    def decode_signed(self, byte_val):
        return byte_val if byte_val < 128 else byte_val - 256
    
    # def encode_table_entry():
    def encode_table_entry(self, parent_state_bytes, move_tuple, g_val, f_val):
        # Encode a table entry with parent, move, g(n), and f(n), seperate by PADDING.
        move_bytes = bytes([ord(move_tuple[0]), self.encode_signed(move_tuple[1]), self.encode_signed(move_tuple[2])]) if move_tuple else b''
        g_bytes = g_val.to_bytes(4, 'little')
        f_bytes = f_val.to_bytes(4, 'little')
        return parent_state_bytes + self.PADDING + move_bytes + self.PADDING + g_bytes + self.PADDING + f_bytes
    
    # def decode_table_entry():
    def decode_table_entry(self, entry_bytes):
        # Decode a table entry into its components.
        parts = entry_bytes.split(self.PADDING)
        parent_bytes = parts[0]
        move_bytes = parts[1]
        g_val = int.from_bytes(parts[2], 'little')
        f_val = int.from_bytes(parts[3], 'little')
        move = None
        if move_bytes:
            move = (chr(move_bytes[0]), self.decode_signed(move_bytes[1]), self.decode_signed(move_bytes[2]))
        return parent_bytes, move, g_val, f_val
    
    # def build_board_2d():
    def build_board_2d(self, state, car_info):
        # Build a 6x6 board from the current state.
        board = [['.' for _ in range(6)] for _ in range(6)]
        for name, x, y in state:
            orient, length = car_info[name]
            if orient == 'H':
                for i in range(length):
                    board[y][x + i] = name
            else:
                for i in range(length):
                    board[y + i][x] = name
        return board
    
    # def compute_blocked_map():
    def compute_blocked_map(self, state, car_info):
        # Compute which rows and columns have car
        blocked_rows = [False] * 6
        blocked_cols = [False] * 6
        for name, x, y in state:
            orient, length = car_info[name]
            if orient == 'H':
                blocked_rows[y] = True
            else:
                blocked_cols[x] = True
        return blocked_rows, blocked_cols

    # precompute_helpful_moves():
    def precompute_helpful_moves(self, state, car_info):
        # Create a default dict to determine current position if moving to new state frees other vehicles(directly or indirectly)
        blocked_rows, blocked_cols = self.compute_blocked_map(state, car_info)
        helpful_moves = defaultdict(dict)
        for name, x, y in state:
            orient, length = car_info[name]
            if orient == 'H':
                for from_x in range(0, 6 - length + 1):
                    for to_x in range(0, 6 - length + 1):
                        if from_x == to_x:
                            continue
                        old_range = [from_x + i for i in range(length)]
                        new_range = [to_x + i for i in range(length)]
                        for col in old_range:
                            if col not in new_range and blocked_cols[col]:
                                helpful_moves[name][(from_x, y, to_x, y)] = True
                                break
            else:
                for from_y in range(0, 6 - length + 1):
                    for to_y in range(0, 6 - length + 1):
                        if from_y == to_y:
                            continue
                        old_range = [from_y + i for i in range(length)]
                        new_range = [to_y + i for i in range(length)]
                        for row in old_range:
                            if row not in new_range and blocked_rows[row]:
                                helpful_moves[name][(x, from_y, x, to_y)] = True
                                break
        return helpful_moves
    
    # relative_helful_move():
    @staticmethod
    # Create a default dict to consider the cases where two cars in the same horizontal or vertical direction create an advantage for the other car.
    def relative_helpful_moves(self, state, car_info):
        helpful = defaultdict(dict)
        for i, (name1, x1, y1) in enumerate(state):
            orient1, len1 = car_info[name1]
            end1_x = x1 + len1 - 1
            end1_y = y1 + len1 - 1
            for j, (name2, x2, y2) in enumerate(state):
                if i == j:
                    continue
                orient2, len2 = car_info[name2]
                end2_x = x2 + len2 - 1
                end2_y = y2 + len2 - 1
                if orient1 != orient2:
                    continue
                if orient1 == 'H' and y1 == y2:
                    if end1_x < x2:
                        for from_x in range(0, 6 - len1 + 1):
                            for to_x in range(0, 6 - len1 + 1):
                                if to_x < from_x:
                                    helpful[name1][(from_x, y1, to_x, y1)] = True
                    elif x1 > end2_x:
                        for from_x in range(0, 6 - len1 + 1):
                            for to_x in range(0, 6 - len1 + 1):
                                if to_x > from_x:
                                    helpful[name1][(from_x, y1, to_x, y1)] = True
                elif orient1 == 'V' and x1 == x2:
                    if end1_y < y2:
                        for from_y in range(0, 6 - len1 + 1):
                            for to_y in range(0, 6 - len1 + 1):
                                if to_y < from_y:
                                    helpful[name1][(x1, from_y, x1, to_y)] = True
                    elif y1 > end2_y:
                        for from_y in range(0, 6 - len1 + 1):
                            for to_y in range(0, 6 - len1 + 1):
                                if to_y > from_y:
                                    helpful[name1][(x1, from_y, x1, to_y)] = True
        return helpful

    
    # generate_successors():
    def generate_successors(self, state, car_info, helpful_moves, relative_moves):
        # Generate all valid moves
        board = self.build_board_2d(state, car_info)
        successors = []

        for car_name, x, y in state:
            orient, length = car_info[car_name]

            for direction in [-1, 1]:
                for step in range(1, 6):
                    if orient == 'H':
                        new_x = x + direction * step
                        new_y = y
                        if new_x < 0 or new_x + length > 6:
                            break
                        if any(board[y][new_x + i] not in ('.', car_name) for i in range(length)):
                            break
                    else:
                        new_x = x
                        new_y = y + direction * step
                        if new_y < 0 or new_y + length > 6:
                            break
                        if any(board[new_y + i][x] not in ('.', car_name) for i in range(length)):
                            break

                    if not (helpful_moves.get(car_name, {}).get((x, y, new_x, new_y), False) or
                        relative_moves.get(car_name, {}).get((x, y, new_x, new_y), False)):
                            continue

                    new_state = []
                    for name, ox, oy in state:
                        if name == car_name:
                            new_state.append((name, new_x, new_y))
                        else:
                            new_state.append((name, ox, oy))
                    new_state = tuple(sorted(new_state))

                    dx = new_x - x
                    dy = new_y - y
                    move = (car_name, dx, dy)
                    cost = abs(dx)*length + abs(dy)*length
                    successors.append((new_state, move, cost))

        return successors
    
    # reconstruct_path():
    def reconstruct_path(self, goal_encoded, table):
        # Return from goal_state to start_state to get list of move
        path = []
        current = goal_encoded
        while current in table:
            entry = table[current]
            parent, move, _, _ = self.decode_table_entry(entry)
            if move:
                path.append(move)
            if parent == b'':
                break
            current = parent
        return path[::-1]
    
    # is_solved:
    def is_solved(self, state, car_info):
        # Check if red car (A) reaches the exit
        for name, x, y in state:
            if name == 'A':
                length = car_info['A'][1]
                return x + length - 1 == 5
        return False

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
        
        # self.clock.startTimer()

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

class AStarStrategy(SolverStrategy, BaseSolver):
    """A* Search strategy"""

    def __init__(self, map_obj, max_time=30):
        super().__init__(map_obj)
        self.max_time = max_time

    def get_name(self):
        return f"A* Search (g(n)={self.max_time}s)"

    def solve(self):
        start_tuple = []
        car_info = {}

        for v in self.map.vehicles:
            a, b = v.change_vehicle_data()
            start_tuple.append(tuple(a))  
            car_info[a[0]] = tuple(b[1:])  

        start_tuple = tuple(sorted(start_tuple))  # đảm bảo thống nhất
        start_state = self.encode_state(start_tuple)
        start_g = 0
        start_h = self.heuristic(start_tuple, car_info)
        start_f = start_g + start_h

        return self.solving_A_star(start_state, start_tuple, car_info, start_g, start_f, max_time=self.max_time)

    def get_blockers(self, name, x, y, car_info, board):
        # Return cars blocking the given car
        direction, length = car_info[name]
        blockers = set()
        if direction == 'H':
            x_end = x + length - 1
            for xi in range(x_end + 1, 6):
                if board[y][xi] != '.' and board[y][xi] != name:
                    blockers.add(board[y][xi])
                    break
        elif direction == 'V':
            y_end = y + length - 1
            for yi in range(y_end + 1, 6):
                if board[yi][x] != '.' and board[yi][x] != name:
                    blockers.add(board[yi][x])
                    break
        return blockers

    def heuristic(self, state, car_info):
        # h(n):HDH
        board = self.build_board_2d(state, car_info)
        for name, x, y in state:
            if name == 'A':
                red_x, red_y = x, y
                red_length = car_info['A'][1]
                break

        dist_to_goal = 5 - (red_x + red_length - 1)
        cost = dist_to_goal * red_length

        visited = set()
        frontier = [('A', red_x, red_y)]

        while frontier:
            current_name, cx, cy = frontier.pop()
            if current_name in visited:
                continue
            visited.add(current_name)

            blockers = self.get_blockers(current_name, cx, cy, car_info, board)
            for b_name in blockers:
                for name2, bx, by in state:
                    if name2 == b_name:
                        direction, length = car_info[b_name]
                        estimated_moves = 1
                        cost += estimated_moves * length
                        frontier.append((b_name, bx, by))
                        break

        return cost
    def solving_A_star(self, start_state, start_tuple, car_info, start_g, start_f, max_time=30):
        # Main A* search loop
        start_time_clock = time.time()
        open_heap = heapdict.heapdict()
        table = {}

        helpful_moves = self.precompute_helpful_moves(start_tuple, car_info)
        relative_moves = self.relative_helpful_moves(start_tuple, car_info)

        open_heap[start_state] = start_f
        table[start_state] = self.encode_table_entry(b'', None, start_g, start_f)
        count = 0
        while open_heap:
            if time.time() - start_time_clock > max_time:
                print("Timed out")
                return []
            parent_state, parent_f = open_heap.popitem()
            parent_tuple = self.decode_state(parent_state)
            _, parent_move, parent_g, _ = self.decode_table_entry(table[parent_state])

            if self.is_solved(parent_tuple, car_info):
                return self.reconstruct_path(parent_state, table)

            for child_tuple, move, step_cost in self.generate_successors(parent_tuple, car_info, helpful_moves, relative_moves):
                if parent_move and move[0] == parent_move[0]:
                    continue
                child_state = self.encode_state(child_tuple)
                child_g = parent_g + step_cost
                if child_state in table:
                    _, _, old_g, _ = self.decode_table_entry(table[child_state])
                    if child_g >= old_g:
                        continue

                child_h = self.heuristic(child_tuple, car_info)
                if (parent_f - parent_g == child_h):
                    _, length_child = car_info[move[0]]
                    child_h = child_h + length_child
                child_f = child_g + child_h

                open_heap[child_state] = child_f
                table[child_state] = self.encode_table_entry(parent_state, move, child_g, child_f)
        return []




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

   