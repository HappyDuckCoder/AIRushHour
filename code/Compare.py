import time
import tracemalloc
import psutil
import os
from collections import defaultdict
import matplotlib.pyplot as plt
from SolverAlgorithms.DFS import DFSStrategy
from SolverAlgorithms.BFS import BFSStrategy

class AlgorithmComparison:
    """Công cụ so sánh hiệu suất các thuật toán giải Rush Hour"""
    
    def __init__(self, map_obj):
        self.map = map_obj
        self.algorithms = {
            'DFS': DFSStrategy,
            'BFS': BFSStrategy
        }
        self.results = defaultdict(dict)
        self.comparison_data = []
    
    def measure_performance(self, algorithm_name, max_depth=50, runs=1):
        """Đo hiệu suất của một thuật toán"""
        algorithm_class = self.algorithms[algorithm_name]
        
        performance_data = {
            'algorithm': algorithm_name,
            'execution_times': [],
            'memory_usage': [],
            'peak_memory': [],
            'solution_lengths': [],
            'states_explored': [],
            'success_rate': 0,
            'average_time': 0,
            'average_memory': 0,
            'average_solution_length': 0,
            'average_states_explored': 0
        }
        
        successful_runs = 0
        
        for run in range(runs):
            print(f"Chạy {algorithm_name} - Lần {run + 1}/{runs}")
            
            # Đo bộ nhớ
            tracemalloc.start()
            process = psutil.Process(os.getpid())
            memory_before = process.memory_info().rss / 1024 / 1024  # MB
            
            # Tạo instance thuật toán
            solver = algorithm_class(self.map, max_depth)
            
            # Đo thời gian thực thi
            start_time = time.time()
            solution = solver.solve()
            end_time = time.time()
            
            execution_time = end_time - start_time
            
            # Đo bộ nhớ sau khi chạy
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            
            memory_after = process.memory_info().rss / 1024 / 1024  # MB
            memory_used = memory_after - memory_before
            peak_memory_mb = peak / 1024 / 1024  # MB
            
            # Lưu kết quả
            performance_data['execution_times'].append(execution_time)
            performance_data['memory_usage'].append(memory_used)
            performance_data['peak_memory'].append(peak_memory_mb)
            
            if solution is not None:
                successful_runs += 1
                performance_data['solution_lengths'].append(len(solution))
                
                # Lấy thông tin từ solver nếu có
                if hasattr(solver, 'get_search_info'):
                    search_info = solver.get_search_info()
                    performance_data['states_explored'].append(search_info.get('states_explored', 0))
                else:
                    performance_data['states_explored'].append(len(solver.table) if hasattr(solver, 'table') else 0)
            else:
                performance_data['solution_lengths'].append(0)
                performance_data['states_explored'].append(len(solver.table) if hasattr(solver, 'table') else 0)
        
        # Tính toán trung bình
        if performance_data['execution_times']:
            performance_data['average_time'] = sum(performance_data['execution_times']) / len(performance_data['execution_times'])
            performance_data['average_memory'] = sum(performance_data['memory_usage']) / len(performance_data['memory_usage'])
            performance_data['average_states_explored'] = sum(performance_data['states_explored']) / len(performance_data['states_explored'])
        
        if successful_runs > 0:
            valid_solutions = [x for x in performance_data['solution_lengths'] if x > 0]
            performance_data['average_solution_length'] = sum(valid_solutions) / len(valid_solutions) if valid_solutions else 0
        
        performance_data['success_rate'] = (successful_runs / runs) * 100
        
        return performance_data
    
    def compare_algorithms(self, max_depth=50, runs=3):
        """So sánh tất cả các thuật toán"""
        print("🔍 Bắt đầu so sánh thuật toán...")
        print("=" * 50)
        
        for algorithm_name in self.algorithms.keys():
            print(f"\n📊 Đang đo hiệu suất {algorithm_name}...")
            
            performance_data = self.measure_performance(algorithm_name, max_depth, runs)
            self.results[algorithm_name] = performance_data
            self.comparison_data.append(performance_data)
        
        return self.results
    
    def print_comparison_report(self):
        """In báo cáo so sánh chi tiết"""
        print("\n" + "=" * 80)
        print("📋 BÁO CÁO SO SÁNH THUẬT TOÁN")
        print("=" * 80)
        
        for algorithm_name, data in self.results.items():
            print(f"\n🔸 {algorithm_name.upper()}")
            print("-" * 40)
            print(f"⏱️  Thời gian trung bình: {data['average_time']:.4f} giây")
            print(f"💾 Bộ nhớ sử dụng: {data['average_memory']:.2f} MB")
            print(f"🎯 Tỷ lệ thành công: {data['success_rate']:.1f}%")
            print(f"📏 Độ dài nghiệm TB: {data['average_solution_length']:.1f} bước")
            print(f"🔍 Số trạng thái khám phá: {data['average_states_explored']:.0f}")
            
            if data['execution_times']:
                print(f"⚡ Thời gian nhanh nhất: {min(data['execution_times']):.4f} giây")
                print(f"🐌 Thời gian chậm nhất: {max(data['execution_times']):.4f} giây")
        
        # So sánh trực tiếp
        print(f"\n🏆 SO SÁNH TRỰC TIẾP")
        print("-" * 40)
        
        if len(self.results) >= 2:
            algorithms = list(self.results.keys())
            dfs_data = self.results.get('DFS', {})
            bfs_data = self.results.get('BFS', {})
            
            if dfs_data and bfs_data:
                # So sánh thời gian
                if dfs_data['average_time'] < bfs_data['average_time']:
                    time_diff = bfs_data['average_time'] - dfs_data['average_time']
                    print(f"⚡ DFS nhanh hơn BFS {time_diff:.4f} giây ({((time_diff/bfs_data['average_time'])*100):.1f}%)")
                else:
                    time_diff = dfs_data['average_time'] - bfs_data['average_time']
                    print(f"⚡ BFS nhanh hơn DFS {time_diff:.4f} giây ({((time_diff/dfs_data['average_time'])*100):.1f}%)")
                
                # So sánh bộ nhớ
                if dfs_data['average_memory'] < bfs_data['average_memory']:
                    memory_diff = bfs_data['average_memory'] - dfs_data['average_memory']
                    print(f"💾 DFS tiết kiệm bộ nhớ hơn BFS {memory_diff:.2f} MB")
                else:
                    memory_diff = dfs_data['average_memory'] - bfs_data['average_memory']
                    print(f"💾 BFS tiết kiệm bộ nhớ hơn DFS {memory_diff:.2f} MB")
                
                # So sánh độ dài nghiệm
                if dfs_data['average_solution_length'] > 0 and bfs_data['average_solution_length'] > 0:
                    if dfs_data['average_solution_length'] < bfs_data['average_solution_length']:
                        step_diff = bfs_data['average_solution_length'] - dfs_data['average_solution_length']
                        print(f"🎯 DFS tìm nghiệm ngắn hơn BFS {step_diff:.1f} bước")
                    elif bfs_data['average_solution_length'] < dfs_data['average_solution_length']:
                        step_diff = dfs_data['average_solution_length'] - bfs_data['average_solution_length']
                        print(f"🎯 BFS tìm nghiệm ngắn hơn DFS {step_diff:.1f} bước")
                    else:
                        print(f"🎯 Cả hai thuật toán tìm nghiệm cùng độ dài")
    
    def generate_performance_chart(self, save_path=None):
        """Tạo biểu đồ so sánh hiệu suất"""
        if not self.comparison_data:
            print("❌ Không có dữ liệu để tạo biểu đồ")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('So sánh hiệu suất thuật toán DFS vs BFS', fontsize=16, fontweight='bold')
        
        algorithms = [data['algorithm'] for data in self.comparison_data]
        
        # Biểu đồ thời gian thực thi
        times = [data['average_time'] for data in self.comparison_data]
        axes[0, 0].bar(algorithms, times, color=['skyblue', 'lightcoral'])
        axes[0, 0].set_title('Thời gian thực thi trung bình')
        axes[0, 0].set_ylabel('Thời gian (giây)')
        
        # Biểu đồ bộ nhớ sử dụng
        memories = [data['average_memory'] for data in self.comparison_data]
        axes[0, 1].bar(algorithms, memories, color=['lightgreen', 'lightyellow'])
        axes[0, 1].set_title('Bộ nhớ sử dụng trung bình')
        axes[0, 1].set_ylabel('Bộ nhớ (MB)')
        
        # Biểu đồ số bước giải
        solution_lengths = [data['average_solution_length'] for data in self.comparison_data]
        axes[1, 0].bar(algorithms, solution_lengths, color=['lightpink', 'lightblue'])
        axes[1, 0].set_title('Độ dài nghiệm trung bình')
        axes[1, 0].set_ylabel('Số bước')
        
        # Biểu đồ số trạng thái khám phá
        states_explored = [data['average_states_explored'] for data in self.comparison_data]
        axes[1, 1].bar(algorithms, states_explored, color=['orange', 'purple'])
        axes[1, 1].set_title('Số trạng thái khám phá')
        axes[1, 1].set_ylabel('Số trạng thái')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"💾 Biểu đồ đã được lưu: {save_path}")
        
        plt.show()
    
    def export_results_to_csv(self, filename="algorithm_comparison.csv"):
        """Xuất kết quả ra file CSV"""
        import csv
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Algorithm', 'Avg_Time', 'Avg_Memory', 'Success_Rate', 
                         'Avg_Solution_Length', 'Avg_States_Explored']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for data in self.comparison_data:
                writer.writerow({
                    'Algorithm': data['algorithm'],
                    'Avg_Time': data['average_time'],
                    'Avg_Memory': data['average_memory'],
                    'Success_Rate': data['success_rate'],
                    'Avg_Solution_Length': data['average_solution_length'],
                    'Avg_States_Explored': data['average_states_explored']
                })
        
        print(f"💾 Kết quả đã được xuất ra: {filename}")

# Hàm tiện ích để chạy so sánh
def compare_algorithms_on_map(map_obj, max_depth=50, runs=3):
    """Hàm tiện ích để so sánh thuật toán trên một map"""
    comparison = AlgorithmComparison(map_obj)
    results = comparison.compare_algorithms(max_depth, runs)
    comparison.print_comparison_report()
    
    # Tạo biểu đồ (nếu có matplotlib)
    try:
        comparison.generate_performance_chart()
    except ImportError:
        print("⚠️ Matplotlib không được cài đặt. Bỏ qua việc tạo biểu đồ.")
    
    # Xuất CSV
    comparison.export_results_to_csv()
    
    return results

# Cách sử dụng:
"""
# Trong GameScreen.py hoặc file chính
from SolverAlgorithms.AlgorithmComparison import compare_algorithms_on_map

# So sánh trên map hiện tại
def compare_current_map(self):
    results = compare_algorithms_on_map(self.map, max_depth=30, runs=5)
    return results

# Hoặc tạo một nút Compare trong UI
self.compare_btn = Button("Compare Algorithms", (50, SCREEN_H - 250), 150, 40, PURPLE)

# Trong handle_event
elif self.compare_btn.hit(event.pos):
    self.compare_current_map()
"""