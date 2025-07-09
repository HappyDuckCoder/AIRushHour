from SolverAlgorithms.DFS import DFSStrategy
from SolverAlgorithms.BFS import BFSStrategy

#==============================================
# Strategy Factory (Optional - for easy creation)
#==============================================
class StrategyFactory:
    """Factory to create different strategies"""
    
    @staticmethod
    def create_dfs(map_obj, max_depth=50):
        return DFSStrategy(map_obj, max_depth)

    def create_bfs(map_obj, max_depth=50):
        return BFSStrategy(map_obj, max_depth)