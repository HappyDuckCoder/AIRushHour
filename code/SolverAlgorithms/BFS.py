from SolverAlgorithms.Solver import SolverStrategy, BaseSolver
from collections import deque

#==============================================
# Concrete Strategy: BFS
#==============================================
class BFSStrategy(SolverStrategy, BaseSolver):
    """Breadth-First Search strategy"""
    
    def __init__(self, map_obj, max_depth=50):
        super().__init__(map_obj)
        self.max_depth = max_depth
        self.table = {}  
        self.solution = []
    
    def get_name(self):
        return f"BFS (max_depth={self.max_depth})"
    
    def bfs(self, initial_vehicles):
        """BFS search for solution"""
        # Queue để lưu trữ các state: (vehicles, path, depth)
        queue = deque([(initial_vehicles, [], 0)])
        
        # Đánh dấu state ban đầu
        initial_state = self.get_state_key(initial_vehicles)
        self.table[initial_state] = {
            'parent_state': None,
            'move': None,
            'g_n': 0,
            'f_n': None,
            'visited': True
        }
        
        while queue:
            current_vehicles, path, depth = queue.popleft()
            
            # Kiểm tra giới hạn độ sâu
            if depth > self.max_depth:
                continue
            
            # Kiểm tra điều kiện kết thúc
            if self.is_solved(current_vehicles):
                self.solution = path[:]
                return True
            
            # Lấy các nước đi có thể
            moves = self.get_possible_moves(current_vehicles)
            
            for move in moves:
                new_vehicles = self.apply_move(current_vehicles, move)
                new_path = path + [move]
                new_depth = depth + 1
                
                state_key = self.get_state_key(new_vehicles)
                
                # Kiểm tra xem state đã được thăm chưa
                if state_key not in self.table:
                    # Thêm state vào table với thông tin chi tiết
                    parent_state = self.get_state_key(current_vehicles)
                    
                    self.table[state_key] = {
                        'parent_state': parent_state,
                        'move': move,
                        'g_n': new_depth,
                        'f_n': None,
                        'visited': True
                    }
                    
                    # Thêm vào queue để tiếp tục tìm kiếm
                    queue.append((new_vehicles, new_path, new_depth))
        
        return False
    
    def solve(self):
        """Solve the puzzle using BFS"""
        self.table.clear()  
        self.solution.clear()
        
        initial_vehicles = [v.copy() for v in self.map.vehicles]
        
        if self.bfs(initial_vehicles):
            return self.solution
        else:
            return None
    
    def get_solution_path(self):
        """Reconstruct solution path from table"""
        if not self.solution:
            return []
        
        return self.solution
    
    def reconstruct_path_from_table(self, goal_state):
        """Tái tạo đường đi từ table (phương pháp thay thế)"""
        path = []
        current_state = goal_state
        
        while current_state is not None:
            state_info = self.table.get(current_state)
            if state_info is None:
                break
                
            move = state_info['move']
            if move is not None:
                path.append(move)
            
            current_state = state_info['parent_state']
        
        # Đảo ngược path vì chúng ta đi từ goal về start
        path.reverse()
        return path
    
    def get_search_info(self):
        """Trả về thông tin về quá trình tìm kiếm"""
        return {
            'algorithm': 'BFS',
            'states_explored': len(self.table),
            'solution_length': len(self.solution) if self.solution else 0,
            'max_depth': self.max_depth
        }