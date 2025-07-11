import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.stdout.reconfigure(encoding='utf-8')

import time
import tracemalloc
import psutil
import os
from collections import defaultdict
import matplotlib.pyplot as plt
import csv
from SolverAlgorithms.DFS import DFSStrategy
from SolverAlgorithms.BFS import BFSStrategy
from SolverAlgorithms.AStarr import AStarStrategy
from SolverAlgorithms.UCS import UCSStrategy
from Game.Map import Map

class AlgorithmComparison:
    """Công cụ so sánh hiệu suất các thuật toán giải Rush Hour"""
    
    def __init__(self, map_obj, map_id=None):
        self.map = map_obj
        self.map_id = map_id
        self.algorithms = {
            'DFS': DFSStrategy,
            'BFS': BFSStrategy,
            'A*': AStarStrategy,
            'UCS': UCSStrategy
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
            'total_costs': [],
            'success_rate': 0,
            'average_time': 0,
            'average_memory': 0,
            'average_solution_length': 0,
            'average_states_explored': 0,
            'average_total_cost': 0
        }
        
        successful_runs = 0
        
        for run in range(runs):
            print(f"Chạy {algorithm_name} - Lần {run + 1}/{runs}")
            
            # Đo bộ nhớ
            tracemalloc.start()
            process = psutil.Process(os.getpid())
            memory_before = process.memory_info().rss / 1024 / 1024  # MB
            
            # Tạo instance thuật toán
            try:
                if algorithm_name == 'DFS':
                    solver = algorithm_class(self.map, max_depth)
                elif algorithm_name == 'BFS':
                    solver = algorithm_class(self.map, max_depth)  
                elif algorithm_name == 'UCS':
                    solver = algorithm_class(self.map)
                elif algorithm_name == 'A*':
                    solver = algorithm_class(self.map, max_time=30)
                else:
                    raise ValueError(f"Thuật toán không được hỗ trợ: {algorithm_name}")
                
                # Đo thời gian thực thi
                start_time = time.time()
                solution, node_expanded, total_cost = solver.solve()
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
                    performance_data['states_explored'].append(node_expanded if node_expanded is not None else 0)
                    performance_data['total_costs'].append(total_cost if total_cost is not None else 0)
                else:
                    performance_data['solution_lengths'].append(0)
                    performance_data['states_explored'].append(node_expanded if node_expanded is not None else 0)
                    performance_data['total_costs'].append(0)
                    
            except Exception as e:
                print(f"⚠️ Lỗi khi chạy {algorithm_name} - Lần {run + 1}: {e}")
                # Dừng tracemalloc nếu có lỗi
                try:
                    tracemalloc.stop()
                except:
                    pass
                # Thêm giá trị mặc định cho lần chạy thất bại
                performance_data['execution_times'].append(0)
                performance_data['memory_usage'].append(0)
                performance_data['peak_memory'].append(0)
                performance_data['solution_lengths'].append(0)
                performance_data['states_explored'].append(0)
                performance_data['total_costs'].append(0)
        
        # Tính toán trung bình
        if performance_data['execution_times']:
            performance_data['average_time'] = sum(performance_data['execution_times']) / len(performance_data['execution_times'])
            performance_data['average_memory'] = sum(performance_data['memory_usage']) / len(performance_data['memory_usage'])
            performance_data['average_states_explored'] = sum(performance_data['states_explored']) / len(performance_data['states_explored'])
            performance_data['average_total_cost'] = sum(performance_data['total_costs']) / len(performance_data['total_costs'])
        
        if successful_runs > 0:
            valid_solutions = [x for x in performance_data['solution_lengths'] if x > 0]
            performance_data['average_solution_length'] = sum(valid_solutions) / len(valid_solutions) if valid_solutions else 0
        
        performance_data['success_rate'] = (successful_runs / runs) * 100
        
        return performance_data
    
    def compare_algorithms(self, max_depth=50, runs=3):
        """So sánh tất cả các thuật toán"""
        print(f"🔍 Bắt đầu so sánh thuật toán cho Map {self.map_id}...")
        print("=" * 50)
        
        for algorithm_name in self.algorithms.keys():
            print(f"\n📊 Đang đo hiệu suất {algorithm_name}...")
            
            performance_data = self.measure_performance(algorithm_name, max_depth, runs)
            self.results[algorithm_name] = performance_data
            self.comparison_data.append(performance_data)
        
        return self.results
    
    def generate_performance_chart(self, save_path=None):
        """Tạo biểu đồ so sánh hiệu suất"""
        if not self.comparison_data:
            print("❌ Không có dữ liệu để tạo biểu đồ")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle(f'So sánh hiệu suất thuật toán - Map {self.map_id}', fontsize=16, fontweight='bold')
        
        algorithms = [data['algorithm'] for data in self.comparison_data]
        
        # Biểu đồ thời gian thực thi
        times = [data['average_time'] for data in self.comparison_data]
        colors = ['skyblue', 'lightcoral', 'lightgreen', 'lightyellow']
        axes[0, 0].bar(algorithms, times, color=colors[:len(algorithms)])
        axes[0, 0].set_title('Thời gian thực thi trung bình')
        axes[0, 0].set_ylabel('Thời gian (giây)')
        
        # Biểu đồ bộ nhớ sử dụng
        memories = [data['average_memory'] for data in self.comparison_data]
        axes[0, 1].bar(algorithms, memories, color=colors[:len(algorithms)])
        axes[0, 1].set_title('Bộ nhớ sử dụng trung bình')
        axes[0, 1].set_ylabel('Bộ nhớ (MB)')
        
        # Biểu đồ số bước giải
        solution_lengths = [data['average_solution_length'] for data in self.comparison_data]
        axes[1, 0].bar(algorithms, solution_lengths, color=colors[:len(algorithms)])
        axes[1, 0].set_title('Độ dài nghiệm trung bình')
        axes[1, 0].set_ylabel('Số bước')
        
        # Biểu đồ số trạng thái khám phá
        states_explored = [data['average_states_explored'] for data in self.comparison_data]
        axes[1, 1].bar(algorithms, states_explored, color=colors[:len(algorithms)])
        axes[1, 1].set_title('Số trạng thái khám phá')
        axes[1, 1].set_ylabel('Số trạng thái')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"💾 Biểu đồ đã được lưu: {save_path}")
        
        plt.close()  # Đóng figure để giải phóng bộ nhớ
    
    def export_results_to_csv(self, filename):
        """Xuất kết quả ra file CSV"""
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Algorithm', 'Avg_Time', 'Avg_Memory', 'Success_Rate', 
                         'Avg_Solution_Length', 'Avg_States_Explored', 'Avg_Total_Cost', 'Map_ID']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for data in self.comparison_data:
                writer.writerow({
                    'Algorithm': data['algorithm'],
                    'Avg_Time': data['average_time'],
                    'Avg_Memory': data['average_memory'],
                    'Success_Rate': data['success_rate'],
                    'Avg_Solution_Length': data['average_solution_length'],
                    'Avg_States_Explored': data['average_states_explored'],
                    'Avg_Total_Cost': data['average_total_cost'],
                    'Map_ID': self.map_id
                })
        
        print(f"💾 Kết quả Map {self.map_id} đã được xuất ra: {filename}")

    def save_text_report(self, filename):
        """Lưu báo cáo text vào file"""
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write(f"📋 BÁO CÁO SO SÁNH THUẬT TOÁN - MAP {self.map_id}\n")
            f.write("=" * 80 + "\n\n")
            
            for algorithm_name, data in self.results.items():
                f.write(f"🔸 {algorithm_name.upper()}\n")
                f.write("-" * 40 + "\n")
                f.write(f"⏱️  Thời gian trung bình: {data['average_time']:.4f} giây\n")
                f.write(f"💾 Bộ nhớ sử dụng: {data['average_memory']:.2f} MB\n")
                f.write(f"🎯 Tỷ lệ thành công: {data['success_rate']:.1f}%\n")
                f.write(f"📏 Độ dài nghiệm TB: {data['average_solution_length']:.1f} bước\n")
                f.write(f"🔍 Số trạng thái khám phá: {data['average_states_explored']:.0f}\n")
                f.write(f"💰 Chi phí trung bình: {data['average_total_cost']:.2f}\n")
                
                if data['execution_times']:
                    f.write(f"⚡ Thời gian nhanh nhất: {min(data['execution_times']):.4f} giây\n")
                    f.write(f"🐌 Thời gian chậm nhất: {max(data['execution_times']):.4f} giây\n")
                f.write("\n")
        
        print(f"💾 Báo cáo Map {self.map_id} đã được lưu: {filename}")


def run_all_comparisons(max_depth=50, runs=3):
    """Chạy so sánh cho tất cả 10 map"""
    print("🚀 Bắt đầu so sánh thuật toán cho tất cả 10 map...")
    print("=" * 80)
    
    # Tạo thư mục kết quả
    results_dir = "code/Comparison/Results"
    os.makedirs(results_dir, exist_ok=True)
    
    all_results = []
    
    for map_id in range(1, 10):
        print(f"\n🗺️  Đang xử lý Map {map_id}...")
        
        try:
            # Tạo map
            game_map = Map()
            game_map.load_level_data_from_file(map_id)
            
            # Tạo comparison object
            comparison = AlgorithmComparison(game_map, map_id)
            
            # Chạy so sánh
            results = comparison.compare_algorithms(max_depth, runs)
            all_results.append((map_id, results))
            
            # Lưu các file kết quả
            base_filename = f"{results_dir}/{map_id:02d}_comparison"
            
            # Lưu báo cáo text
            comparison.save_text_report(f"{base_filename}.txt")
            
            # Lưu CSV
            comparison.export_results_to_csv(f"{base_filename}.csv")
            
            # Tạo và lưu biểu đồ
            try:
                comparison.generate_performance_chart(f"{base_filename}_chart.png")
            except Exception as e:
                print(f"⚠️ Không thể tạo biểu đồ cho Map {map_id}: {e}")
            
            print(f"✅ Hoàn thành Map {map_id}")
            
        except Exception as e:
            print(f"❌ Lỗi khi xử lý Map {map_id}: {e}")
            continue
    
    # Tạo báo cáo tổng hợp
    create_summary_report(all_results, results_dir)
    
    print(f"\n🎉 Hoàn thành so sánh cho tất cả map!")
    print(f"📁 Kết quả được lưu trong thư mục: {results_dir}")
    
    return all_results


def create_summary_report(all_results, results_dir):
    """Tạo báo cáo tổng hợp cho tất cả map"""
    summary_file = f"{results_dir}/00_summary_report.txt"
    
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("🏆 BÁO CÁO TỔNG HỢP - TẤT CẢ MAP\n")
        f.write("=" * 80 + "\n\n")
        
        # Bảng tóm tắt
        f.write("📊 BẢNG TÓM TẮT HIỆU SUẤT\n")
        f.write("-" * 80 + "\n")
        f.write(f"{'Map':<5} {'DFS Time':<10} {'BFS Time':<10} {'A* Time':<10} {'UCS Time':<10} {'Winner':<10}\n")
        f.write("-" * 80 + "\n")
        
        for map_id, results in all_results:
            if results:
                dfs_time = results.get('DFS', {}).get('average_time', 0)
                bfs_time = results.get('BFS', {}).get('average_time', 0)
                astar_time = results.get('A*', {}).get('average_time', 0)
                ucs_time = results.get('UCS', {}).get('average_time', 0)
                
                # Tìm thuật toán nhanh nhất
                times = {'DFS': dfs_time, 'BFS': bfs_time, 'A*': astar_time, 'UCS': ucs_time}
                winner = min(times, key=times.get) if any(times.values()) else 'N/A'
                
                f.write(f"{map_id:<5} {dfs_time:<10.4f} {bfs_time:<10.4f} {astar_time:<10.4f} {ucs_time:<10.4f} {winner:<10}\n")
        
        f.write("\n")
        
        # Thống kê tổng thể
        f.write("📈 THỐNG KÊ TỔNG THỂ\n")
        f.write("-" * 40 + "\n")
        
        algorithm_wins = {'DFS': 0, 'BFS': 0, 'A*': 0, 'UCS': 0}
        
        for map_id, results in all_results:
            if results:
                times = {}
                for alg in ['DFS', 'BFS', 'A*', 'UCS']:
                    if alg in results and results[alg].get('average_time', 0) > 0:
                        times[alg] = results[alg]['average_time']
                
                if times:
                    winner = min(times, key=times.get)
                    algorithm_wins[winner] += 1
        
        f.write(f"🏆 Số lần thắng:\n")
        for alg, wins in algorithm_wins.items():
            f.write(f"   {alg}: {wins} lần\n")
    
    print(f"💾 Báo cáo tổng hợp đã được lưu: {summary_file}")


if __name__ == "__main__":
    # Chạy so sánh cho tất cả 10 map
    run_all_comparisons(
        max_depth=50,   # độ sâu tối đa
        runs=3          # số lần chạy mỗi thuật toán
    )