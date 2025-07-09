from SolverAlgorithms.Solver import SolverStrategy, BaseSolver
import heapq

#==============================================
# Concrete Strategy: UCS with Vehicle Length Cost
#==============================================
class UCSStrategy(SolverStrategy, BaseSolver):
    """Uniform Cost Search strategy with vehicle length-based cost"""
    
    def __init__(self, map_obj):
        super().__init__(map_obj)
        self.table = {}  
        self.solution = []
    
    def get_name(self):
        return "UCS"
    
    def get_move_cost(self, vehicle):
        """Calculate cost based on vehicle length"""
        return vehicle.length
    
    def ucs(self):
        """UCS search for solution with vehicle length-based cost"""
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
                
                # Tính cost dựa trên độ dài xe
                vehicle_id = move['vehicle_id']  # Giả sử move có vehicle_id
                moved_vehicle = None
                for vehicle in current_vehicles:
                    if vehicle.id == vehicle_id:
                        moved_vehicle = vehicle
                        break
                
                if moved_vehicle:
                    move_cost = self.get_move_cost(moved_vehicle)
                else:
                    move_cost = 1  # Fallback cost
                
                new_cost = current_cost + move_cost
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
        """Solve the puzzle using UCS with vehicle length-based cost"""
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
    
    def get_solution_cost(self):
        """Calculate total cost of solution"""
        if not self.solution:
            return 0
        
        total_cost = 0
        current_vehicles = [v.copy() for v in self.map.vehicles]
        
        for move in self.solution:
            # Tìm xe được di chuyển
            vehicle_id = move['vehicle_id']
            moved_vehicle = None
            for vehicle in current_vehicles:
                if vehicle.id == vehicle_id:
                    moved_vehicle = vehicle
                    break
            
            if moved_vehicle:
                total_cost += self.get_move_cost(moved_vehicle)
            
            # Cập nhật state cho bước tiếp theo
            current_vehicles = self.apply_move(current_vehicles, move)
        
        return total_cost
    
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
        solution_cost = self.get_solution_cost()
        
        return {
            'total_states_generated': total_states,
            'states_visited': visited_states,
            'solution_length': len(self.solution) if self.solution else 0,
            'solution_cost': solution_cost,
            'average_cost_per_move': solution_cost / len(self.solution) if self.solution else 0
        }
    
    def print_solution_details(self):
        """In chi tiết về solution bao gồm cost của từng bước"""
        if not self.solution:
            print("No solution found")
            return
        
        print(f"Solution found with {len(self.solution)} moves:")
        print(f"Total cost: {self.get_solution_cost()}")
        print("\nMove details:")
        
        current_vehicles = [v.copy() for v in self.map.vehicles]
        total_cost = 0
        
        for i, move in enumerate(self.solution):
            # Tìm xe được di chuyển
            vehicle_id = move['vehicle_id']
            moved_vehicle = None
            for vehicle in current_vehicles:
                if vehicle.id == vehicle_id:
                    moved_vehicle = vehicle
                    break
            
            if moved_vehicle:
                move_cost = self.get_move_cost(moved_vehicle)
                total_cost += move_cost
                print(f"Move {i+1}: Vehicle {vehicle_id} (length {moved_vehicle.length}) - Cost: {move_cost}")
            
            # Cập nhật state cho bước tiếp theo
            current_vehicles = self.apply_move(current_vehicles, move)
        
        print(f"\nTotal cost: {total_cost}")