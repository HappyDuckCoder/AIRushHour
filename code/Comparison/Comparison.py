import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.stdout.reconfigure(encoding='utf-8')

import time
import tracemalloc
import psutil
from abc import ABC, abstractmethod
from collections import defaultdict
from typing import List, Optional, Any
import matplotlib.pyplot as plt
import csv
from SolverAlgorithms.DFS import DFSStrategy
from SolverAlgorithms.BFS import BFSStrategy
from SolverAlgorithms.AStarr import AStarStrategy
from SolverAlgorithms.UCS import UCSStrategy
from Game.Map import Map


class PerformanceMetrics:
    """Data class để lưu trữ các metrics hiệu suất"""
    
    def __init__(self, algorithm_name: str):
        self.algorithm = algorithm_name
        self.execution_times = []
        self.memory_usage = []
        self.peak_memory = []
        self.solution_lengths = []
        self.states_explored = []
        self.total_costs = []
        
    def calculate_averages(self, successful_runs: int, total_runs: int):
        """Tính toán các giá trị trung bình"""
        result = {}
        result['algorithm'] = self.algorithm
        
        if self.execution_times:
            result['average_time'] = sum(self.execution_times) / len(self.execution_times)
        else:
            result['average_time'] = 0
            
        if self.memory_usage:
            result['average_memory'] = sum(self.memory_usage) / len(self.memory_usage)
        else:
            result['average_memory'] = 0
            
        if self.states_explored:
            result['average_states_explored'] = sum(self.states_explored) / len(self.states_explored)
        else:
            result['average_states_explored'] = 0
            
        if self.total_costs:
            result['average_total_cost'] = sum(self.total_costs) / len(self.total_costs)
        else:
            result['average_total_cost'] = 0
            
        valid_solution_lengths = [x for x in self.solution_lengths if x > 0]
        if valid_solution_lengths:
            result['average_solution_length'] = sum(valid_solution_lengths) / len(valid_solution_lengths)
        else:
            result['average_solution_length'] = 0
            
        if total_runs > 0:
            result['success_rate'] = (successful_runs / total_runs) * 100
        else:
            result['success_rate'] = 0
            
        if self.execution_times:
            result['min_time'] = min(self.execution_times)
            result['max_time'] = max(self.execution_times)
        else:
            result['min_time'] = 0
            result['max_time'] = 0
            
        return result


class AlgorithmFactory:
    """Factory Pattern để tạo các algorithm instances"""
    
    @staticmethod
    def create_algorithm(algorithm_name: str, game_map: Map, max_time: int = 30):
        """Tạo algorithm instance dựa trên tên"""
        if algorithm_name == 'DFS':
            return DFSStrategy(game_map, max_time)
        elif algorithm_name == 'BFS':
            return BFSStrategy(game_map, max_time)
        elif algorithm_name == 'UCS':
            return UCSStrategy(game_map, max_time)
        elif algorithm_name == 'A*':
            return AStarStrategy(game_map, max_time=max_time)
        else:
            raise ValueError(f"Thuật toán không được hỗ trợ: {algorithm_name}")


class ReportGenerator(ABC):
    """Abstract base class cho các loại report generators"""
    
    @abstractmethod
    def generate_report(self, results, map_id: int, output_path: str):
        """Tạo báo cáo"""
        pass


class TextReportGenerator(ReportGenerator):
    """Concrete implementation cho text report"""
    
    def generate_report(self, results, map_id: int, output_path: str):
        """Tạo báo cáo text"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write(f"BAO CAO SO SANH THUAT TOAN - MAP {map_id}\n")
            f.write("=" * 80 + "\n\n")
            
            for algorithm_name, data in results.items():
                f.write(f"{algorithm_name.upper()}\n")
                f.write("-" * 40 + "\n")
                f.write(f"Thời gian trung bình: {data['average_time']:.4f} giây\n")
                f.write(f"Bộ nhớ sử dụng: {data['average_memory']:.2f} MB\n")
                f.write(f"Tỷ lệ thành công: {data['success_rate']:.1f}%\n")
                f.write(f"Độ dài nghiệm TB: {data['average_solution_length']:.1f} bước\n")
                f.write(f"Số trạng thái khám phá: {data['average_states_explored']:.0f}\n")
                f.write(f"Chi phí trung bình: {data['average_total_cost']:.2f}\n")
                f.write(f"Thời gian nhanh nhất: {data['min_time']:.4f} giây\n")
                f.write(f"Thời gian chậm nhất: {data['max_time']:.4f} giây\n")
                f.write("\n")
        
        print(f"Báo cáo Map {map_id} đã được lưu: {output_path}")


class CSVReportGenerator(ReportGenerator):
    """Concrete implementation cho CSV report"""
    
    def generate_report(self, results, map_id: int, output_path: str):
        """Tạo báo cáo CSV"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Algorithm', 'Avg_Time', 'Avg_Memory', 'Success_Rate', 
                         'Avg_Solution_Length', 'Avg_States_Explored', 'Avg_Total_Cost', 'Map_ID']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for algorithm_name, data in results.items():
                writer.writerow({
                    'Algorithm': algorithm_name,
                    'Avg_Time': data['average_time'],
                    'Avg_Memory': data['average_memory'],
                    'Success_Rate': data['success_rate'],
                    'Avg_Solution_Length': data['average_solution_length'],
                    'Avg_States_Explored': data['average_states_explored'],
                    'Avg_Total_Cost': data['average_total_cost'],
                    'Map_ID': map_id
                })
        
        print(f"Kết quả Map {map_id} đã được xuất ra: {output_path}")


class ChartGenerator(ReportGenerator):
    """Concrete implementation cho chart generation"""
    
    def generate_report(self, results, map_id: int, output_path: str):
        """Tạo biểu đồ so sánh"""
        if not results:
            print("Không có dữ liệu để tạo biểu đồ")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle(f'So sánh hiệu suất thuật toán - Map {map_id}', fontsize=16, fontweight='bold')
        
        algorithms = list(results.keys())
        colors = ['skyblue', 'lightcoral', 'lightgreen', 'lightyellow']
        
        # Biểu đồ thời gian thực thi
        times = [results[alg]['average_time'] for alg in algorithms]
        axes[0, 0].bar(algorithms, times, color=colors[:len(algorithms)])
        axes[0, 0].set_title('Thời gian thực thi trung bình')
        axes[0, 0].set_ylabel('Thời gian (giây)')
        
        # Biểu đồ bộ nhớ sử dụng
        memories = [results[alg]['average_memory'] for alg in algorithms]
        axes[0, 1].bar(algorithms, memories, color=colors[:len(algorithms)])
        axes[0, 1].set_title('Bộ nhớ sử dụng trung bình')
        axes[0, 1].set_ylabel('Bộ nhớ (MB)')
        
        # Biểu đồ số bước giải
        solution_lengths = [results[alg]['average_solution_length'] for alg in algorithms]
        axes[1, 0].bar(algorithms, solution_lengths, color=colors[:len(algorithms)])
        axes[1, 0].set_title('Độ dài nghiệm trung bình')
        axes[1, 0].set_ylabel('Số bước')
        
        # Biểu đồ số trạng thái khám phá
        states_explored = [results[alg]['average_states_explored'] for alg in algorithms]
        axes[1, 1].bar(algorithms, states_explored, color=colors[:len(algorithms)])
        axes[1, 1].set_title('Số trạng thái khám phá')
        axes[1, 1].set_ylabel('Số trạng thái')
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Biểu đồ đã được lưu: {output_path}")


class AlgorithmComparison:
    """Main class để so sánh các thuật toán"""
    
    def __init__(self, game_map: Map, map_id: Optional[int] = None):
        self.map = game_map
        self.map_id = map_id
        self.algorithms = ['DFS', 'BFS', 'A*', 'UCS']
        self.report_generators = {
            'text': TextReportGenerator(),
            'csv': CSVReportGenerator(),
            'chart': ChartGenerator()
        }
    
    def measure_single_run(self, algorithm_name: str, max_time: int = 30):
        """Đo performance một lần chạy"""
        # Preparation
        solver = AlgorithmFactory.create_algorithm(algorithm_name, self.map, max_time)
        
        # Dọn dẹp bộ nhớ trước khi đo
        import gc
        gc.collect()
        
        # Memory measurement setup 
        tracemalloc.start()
        
        # Execution
        start_time = time.time()
        solution, node_expanded, total_cost = solver.solve()
        end_time = time.time()
        
        # Memory measurement cleanup
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
                
        # Calculate metrics
        execution_time = end_time - start_time
        
        # Sử dụng peak memory từ tracemalloc 
        memory_used = max(0, peak / 1024 / 1024)
        
        peak_memory_mb = max(0, peak / 1024 / 1024)
        
        return solution, execution_time, memory_used, peak_memory_mb, node_expanded or 0, total_cost or 0
    
    def measure_algorithm_performance(self, algorithm_name: str, max_time: int = 30, runs: int = 1):
        """Đo hiệu suất của một thuật toán"""
        metrics = PerformanceMetrics(algorithm_name)
        successful_runs = 0
        
        for run in range(runs):
            print(f"Chạy {algorithm_name} - Lần {run + 1}/{runs}")
            
            try:
                solution, execution_time, memory_used, peak_memory, node_expanded, total_cost = \
                    self.measure_single_run(algorithm_name, max_time)
                
                metrics.execution_times.append(execution_time)
                metrics.memory_usage.append(memory_used)
                metrics.peak_memory.append(peak_memory)
                metrics.states_explored.append(node_expanded)
                metrics.total_costs.append(total_cost)
                
                if solution is not None:
                    successful_runs += 1
                    metrics.solution_lengths.append(len(solution))
                else:
                    metrics.solution_lengths.append(0)
                    
            except Exception as e:
                print(f"Lỗi khi chạy {algorithm_name} - Lần {run + 1}: {e}")
                # Thêm giá trị mặc định cho lần chạy thất bại
                metrics.execution_times.append(0)
                metrics.memory_usage.append(0)
                metrics.peak_memory.append(0)
                metrics.solution_lengths.append(0)
                metrics.states_explored.append(0)
                metrics.total_costs.append(0)
        
        return metrics.calculate_averages(successful_runs, runs)
    
    def compare_all_algorithms(self, max_time: int = 30, runs: int = 3):
        """So sánh tất cả các thuật toán"""
        print(f"Bắt đầu so sánh thuật toán cho Map {self.map_id}...")
        print("=" * 50)
        
        results = {}
        
        for algorithm_name in self.algorithms:
            print(f"\nĐang đo hiệu suất {algorithm_name}...")
            results[algorithm_name] = self.measure_algorithm_performance(algorithm_name, max_time, runs)
        
        return results
    
    def generate_reports(self, results, output_dir: str):
        """Tạo tất cả các loại báo cáo"""
        base_filename = f"{output_dir}/{self.map_id:02d}_comparison"
        
        # Tạo text report
        self.report_generators['text'].generate_report(
            results, self.map_id, f"{base_filename}.txt"
        )
        
        # Tạo CSV report
        self.report_generators['csv'].generate_report(
            results, self.map_id, f"{base_filename}.csv"
        )
        
        # Tạo chart
        try:
            self.report_generators['chart'].generate_report(
                results, self.map_id, f"{base_filename}_chart.png"
            )
        except Exception as e:
            print(f"Không thể tạo biểu đồ cho Map {self.map_id}: {e}")


class ComparisonManager:
    """Manager class để quản lý toàn bộ quá trình so sánh"""
    
    def __init__(self, results_dir: str = "code/Comparison/Results"):
        self.results_dir = results_dir
        os.makedirs(self.results_dir, exist_ok=True)
    
    def run_all_comparisons(self, max_time: int = 30, runs: int = 3):
        """Chạy so sánh cho tất cả các map"""
        print("Bắt đầu so sánh thuật toán cho tất cả 10 map...")
        print("=" * 80)
        
        all_results = []
        
        for map_id in range(1, 10):
            print(f"\nĐang xử lý Map {map_id}...")
            
            try:
                # Tạo map
                game_map = Map()
                game_map.load_level_data_from_file(map_id)
                
                # Tạo comparison object
                comparison = AlgorithmComparison(game_map, map_id)
                
                # Chạy so sánh
                results = comparison.compare_all_algorithms(max_time, runs)
                map_result = [map_id, results]
                all_results.append(map_result)
                
                # Tạo báo cáo
                comparison.generate_reports(results, self.results_dir)
                
                print(f"Hoàn thành Map {map_id}")
                
            except Exception as e:
                print(f"Lỗi khi xử lý Map {map_id}: {e}")
                continue
        
        # Tạo báo cáo tổng hợp
        self._create_summary_report(all_results)
        
        print(f"\nHoàn thành so sánh cho tất cả map!")
        print(f"Kết quả được lưu trong thư mục: {self.results_dir}")
        
        return all_results
    
    def _create_summary_report(self, all_results):
        """Tạo báo cáo tổng hợp"""
        summary_file = f"{self.results_dir}/00_summary_report.txt"
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("BAO CAO TONG HOP - TAT CA MAP\n")
            f.write("=" * 80 + "\n\n")
            
            # Bảng tóm tắt
            f.write("BANG TOM TAT HIEU SUAT\n")
            f.write("-" * 80 + "\n")
            f.write(f"{'Map':<5} {'DFS Time':<10} {'BFS Time':<10} {'A* Time':<10} {'UCS Time':<10} {'Winner':<10}\n")
            f.write("-" * 80 + "\n")
            
            algorithm_wins = {'DFS': 0, 'BFS': 0, 'A*': 0, 'UCS': 0}
            
            for map_result in all_results:
                map_id = map_result[0]
                results = map_result[1]
                
                if results:
                    times = {}
                    for alg in ['DFS', 'BFS', 'A*', 'UCS']:
                        times[alg] = results[alg]['average_time']
                    
                    winner = 'N/A'
                    if any(times.values()):
                        min_time = min(times.values())
                        for alg, time_val in times.items():
                            if time_val == min_time:
                                winner = alg
                                break
                    
                    if winner != 'N/A':
                        algorithm_wins[winner] += 1
                    
                    f.write(f"{map_id:<5} {times['DFS']:<10.4f} {times['BFS']:<10.4f} {times['A*']:<10.4f} {times['UCS']:<10.4f} {winner:<10}\n")
            
            f.write("\n")
            
            # Thống kê tổng thể
            f.write("THONG KE TONG THE\n")
            f.write("-" * 40 + "\n")
            f.write("Số lần thắng:\n")
            for alg, wins in algorithm_wins.items():
                f.write(f"   {alg}: {wins} lần\n")
        
        print(f"Báo cáo tổng hợp đã được lưu: {summary_file}")


if __name__ == "__main__":
    # Chạy so sánh cho tất cả map
    manager = ComparisonManager()
    results = manager.run_all_comparisons(
        max_time=30,   
        runs=3          # số lần chạy mỗi thuật toán
    )