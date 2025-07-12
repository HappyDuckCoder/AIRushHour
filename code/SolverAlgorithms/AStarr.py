from SolverAlgorithms.Solver import SolverStrategy, BaseSolver
import heapdict
from collections import defaultdict
import time


class AStarStrategy(SolverStrategy, BaseSolver):

    def __init__(self, map_obj, max_time=30):
        super().__init__(map_obj)
        self.max_time = max_time
        self.PADDING = bytes([220])
        self.total_nodes_expanded = 0
        self.total_cost = 0

    def encode_state(self, state_tuple):
        return b''.join(bytes([ord(name), x, y]) for name, x, y in state_tuple)
    
    def decode_state(self, state_bytes):
        return [(chr(state_bytes[i]), state_bytes[i+1], state_bytes[i+2]) for i in range(0, len(state_bytes), 3)]
    
    def encode_signed(self, val):
        return val % 256

    def decode_signed(self, byte_val):
        if byte_val >= 128 and byte_val != 220:
            return byte_val - 256
        return byte_val
    
    def encode_table_entry(self, parent_state_bytes, move_tuple, g_val, f_val):
        move_bytes = bytes([ord(move_tuple[0]), self.encode_signed(move_tuple[1]), self.encode_signed(move_tuple[2])]) if move_tuple else b''
        g_bytes = g_val.to_bytes(4, 'little')
        f_bytes = f_val.to_bytes(4, 'little')
        return parent_state_bytes + self.PADDING + move_bytes + self.PADDING + g_bytes + self.PADDING + f_bytes
    
    def decode_table_entry(self, entry_bytes):
        parts = entry_bytes.split(self.PADDING)
        parent_bytes = parts[0]
        move_bytes = parts[1]
        g_val = int.from_bytes(parts[2], 'little')
        f_val = int.from_bytes(parts[3], 'little')
        move = None
        if move_bytes:
            move = (chr(move_bytes[0]), self.decode_signed(move_bytes[1]), self.decode_signed(move_bytes[2]))
        return parent_bytes, move, g_val, f_val
    
    def build_board_2d(self, state, car_info):
        board = [['.' for _ in range(6)] for _ in range(6)]
        for name, x, y in state:
            orient, length = car_info[name]
            if orient == 'h':
                for i in range(length):
                    board[y][x + i] = name
            else:
                for i in range(length):
                    board[y + i][x] = name
        return board
    
    def generate_successors(self, state, car_info):
        board = self.build_board_2d(state, car_info)
        successors = []

        for car_name, x, y in state:
            orient, length = car_info[car_name]

            for direction in [-1, 1]:
                for step in range(1, 6):
                    if orient == 'h':
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
    
    def expand_path(self, path):
        expanded = []
        for name, dx, dy in path:
            if dx != 0:
                step = 1 if dx > 0 else -1
                for _ in range(abs(dx)):
                    expanded.append((name, step, 0))
            elif dy != 0:
                step = 1 if dy > 0 else -1
                for _ in range(abs(dy)):
                    expanded.append((name, 0, step))
        return expanded

    def reconstruct_path(self, goal_encoded, table):
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
        return self.expand_path(path[::-1])
    
    def is_solved(self, state, car_info):
        for name, x, y in state:
            if name == 'A':
                length = car_info['A'][1]
                return x + length - 1 == 5
        return False

    def get_name(self):
        return f"A* Search (g(n)={self.max_time}s)"

    def solve(self):
        start_tuple = []
        car_info = {}

        for v in self.map.vehicles:
            a, b = v.change_vehicle_data()
            start_tuple.append(tuple(a))  
            car_info[a[0]] = (b[1].lower(), b[2])  
        start_tuple = tuple(sorted(start_tuple))  
        start_state = self.encode_state(start_tuple)
        start_g = 0
        start_h = self.heuristic(start_tuple, car_info)
        start_f = start_g + start_h

        return self.solving_A_star(start_state, start_tuple, car_info, start_g, start_f, max_time=self.max_time)

    def get_blockers(self, name, x, y, car_info, board):
        direction, length = car_info[name]
        blockers = set()
        if direction == 'h':
            x_end = x + length - 1
            for xi in range(x_end + 1, 6):
                if board[y][xi] != '.' and board[y][xi] != name:
                    blockers.add(board[y][xi])
                    break
        elif direction == 'v':
            y_end = y + length - 1
            for yi in range(y_end + 1, 6):
                if board[yi][x] != '.' and board[yi][x] != name:
                    blockers.add(board[yi][x])
                    break
        return blockers

    def heuristic(self, state, car_info):
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
        start_time_clock = time.time()
        open_heap = heapdict.heapdict()
        table = {}

        open_heap[start_state] = start_f
        table[start_state] = self.encode_table_entry(b'', None, start_g, start_f)
        count = 0
        while open_heap:
            count += 1
            if time.time() - start_time_clock > max_time:
                print("Timed out")
                return []
            parent_state, parent_f = open_heap.popitem()
            parent_tuple = self.decode_state(parent_state)
            _, parent_move, parent_g, _ = self.decode_table_entry(table[parent_state])

            if self.is_solved(parent_tuple, car_info):
                _, _, gn, _  = self.decode_table_entry(table[parent_state])
                return self.reconstruct_path(parent_state, table), count, gn
            
            for child_tuple, move, step_cost in self.generate_successors(parent_tuple, car_info):
                if parent_move and move[0] == parent_move[0]:
                    continue
                child_state = self.encode_state(child_tuple)
                child_g = parent_g + step_cost
                if child_state in table:
                    _, _, old_g, _ = self.decode_table_entry(table[child_state])
                    if child_g >= old_g:
                        continue

                child_h = self.heuristic(child_tuple, car_info)
                child_f = child_g + child_h
                open_heap[child_state] = child_f
                table[child_state] = self.encode_table_entry(parent_state, move, child_g, child_f)
        return [], 0, 0