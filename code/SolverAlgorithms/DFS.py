from SolverAlgorithms.Solver import SolverStrategy, BaseSolver

#==============================================
# Concrete Strategy: DFS
#==============================================
class DFSStrategy(SolverStrategy, BaseSolver):
    """Depth-First Search strategy"""
    
    def __init__(self, map_obj, max_depth=50):
        super().__init__(map_obj)
        self.max_depth = max_depth
        self.table = {}  # Thay thế self.visited = set() bằng table
        self.solution = []
    
    def get_name(self):
        return f"DFS (max_depth={self.max_depth})"
    
    def dfs(self, vehicles, path, depth=0):
        """DFS search for solution"""
        if depth > self.max_depth:
            return False
            
        state_key = self.get_state_key(vehicles)
        
        # Kiểm tra xem state đã được thăm chưa
        if state_key in self.table:
            return False
        
        # Thêm state vào table với thông tin chi tiết
        parent_state = None
        move = None
        if path:
            # Tạo parent state từ path trước đó
            parent_vehicles = [v.copy() for v in self.map.vehicles]
            for prev_move in path[:-1]:
                parent_vehicles = self.apply_move(parent_vehicles, prev_move)
            parent_state = self.get_state_key(parent_vehicles)
            move = path[-1]
        
        # Lưu thông tin state vào table
        self.table[state_key] = {
            'parent_state': parent_state,
            'move': move,
            'g_n': None, 
            'f_n': None, 
            'visited': True
        }
        
        # Kiểm tra điều kiện kết thúc
        if self.is_solved(vehicles):
            self.solution = path[:]
            return True
        
        # Lấy các nước đi có thể
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
        self.table.clear()  
        self.solution.clear()
        
        initial_vehicles = [v.copy() for v in self.map.vehicles]
        
        if self.dfs(initial_vehicles, [], 0):
            return self.solution
        else:
            return None
    
    def get_solution_path(self):
        """Reconstruct solution path from table (nếu cần)"""
        if not self.solution:
            return []
        
        # Có thể sử dụng table để tái tạo đường đi nếu cần
        return self.solution
    
    def get_statistics(self):
        """Get search statistics"""
        return {
            'states_explored': len(self.table),
            'solution_length': len(self.solution) if self.solution else 0
        }