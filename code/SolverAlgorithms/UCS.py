from SolverAlgorithms.Solver import SolverStrategy, BaseSolver
import heapq

#==============================================
# Concrete Strategy: UCS
#==============================================
class UCSStrategy(SolverStrategy, BaseSolver):
    """Uniform Cost Search strategy"""
    
    def __init__(self, map_obj):
        super().__init__(map_obj)
        self.table = {}  
        self.solution = []
    
    def get_name(self):
        return "UCS"
    
    def ucs(self):
        """UCS search for solution"""
        initial_vehicles = [v.copy() for v in self.map.vehicles]
        initial_state = self.get_state_key(initial_vehicles)
        
        # Priority queue: (cost, state_key, vehicles, path)
        # Sử dụng counter để tránh so sánh vehicles khi cost bằng nhau
        counter = 0
        frontier = [(0, counter, initial_state, initial_vehicles, [])]
        heapq.heapify(frontier)
        
        # Khởi tạo bảng với state ban đầu
        self.table[initial_state] = {
            'parent_state': None,
            'move': None,
            'g_n': 0,
            'f_n': 0,
            'visited': False
        }
        
        while frontier:
            current_cost, _, current_state_key, current_vehicles, current_path = heapq.heappop(frontier)
            
            # Kiểm tra nếu state đã được thăm với cost thấp hơn
            if self.table[current_state_key]['visited']:
                continue
            
            # Đánh dấu state đã thăm
            self.table[current_state_key]['visited'] = True
            
            # Kiểm tra điều kiện kết thúc
            if self.is_solved(current_vehicles):
                self.solution = current_path[:]
                return True
            
            # Lấy các nước đi có thể
            moves = self.get_possible_moves(current_vehicles)
            
            for move in moves:
                new_vehicles = self.apply_move(current_vehicles, move)
                new_state_key = self.get_state_key(new_vehicles)
                new_cost = current_cost + 1  # Mỗi nước đi có cost = 1
                new_path = current_path + [move]
                
                # Kiểm tra nếu state chưa được khám phá hoặc tìm thấy đường đi tốt hơn
                if (new_state_key not in self.table or 
                    (not self.table[new_state_key]['visited'] and 
                     new_cost < self.table[new_state_key]['g_n'])):
                    
                    # Cập nhật hoặc thêm state vào table
                    self.table[new_state_key] = {
                        'parent_state': current_state_key,
                        'move': move,
                        'g_n': new_cost,
                        'f_n': new_cost,  # Trong UCS, f(n) = g(n)
                        'visited': False
                    }
                    
                    # Thêm vào frontier
                    counter += 1
                    heapq.heappush(frontier, (new_cost, counter, new_state_key, new_vehicles, new_path))
        
        return False
    
    def solve(self):
        """Solve the puzzle using UCS"""
        self.table.clear()  
        self.solution.clear()
        
        if self.ucs():
            return self.solution
        else:
            return None
    
    def get_solution_path(self):
        """Reconstruct solution path from table"""
        if not self.solution:
            return []
        
        return self.solution
    
    def reconstruct_path_from_table(self):
        """Tái tạo đường đi từ table (phương pháp thay thế)"""
        if not self.table:
            return []
        
        # Tìm state đích (state cuối cùng được thăm và là solution)
        goal_state = None
        for state_key, state_info in self.table.items():
            if state_info['visited']:
                # Tạo vehicles từ state_key để kiểm tra
                vehicles = self.state_key_to_vehicles(state_key)
                if self.is_solved(vehicles):
                    goal_state = state_key
                    break
        
        if not goal_state:
            return []
        
        # Tái tạo đường đi từ goal về start
        path = []
        current_state = goal_state
        
        while current_state and self.table[current_state]['parent_state']:
            move = self.table[current_state]['move']
            if move:
                path.append(move)
            current_state = self.table[current_state]['parent_state']
        
        # Đảo ngược để có đường đi từ start đến goal
        path.reverse()
        return path
    
    def state_key_to_vehicles(self, state_key):
        """Chuyển đổi state_key về vehicles (cần implement tùy theo cách encode state_key)"""
        # Phương thức này cần được implement dựa trên cách encode state_key
        # trong BaseSolver.get_state_key()
        pass
    
    def get_search_statistics(self):
        """Lấy thống kê về quá trình tìm kiếm"""
        total_states = len(self.table)
        visited_states = sum(1 for state_info in self.table.values() if state_info['visited'])
        
        return {
            'total_states_generated': total_states,
            'states_visited': visited_states,
            'solution_length': len(self.solution) if self.solution else 0,
            'solution_cost': len(self.solution) if self.solution else float('inf')
        }