from SolverAlgorithms.DFS import DFSStrategy
from SolverAlgorithms.BFS import BFSStrategy
from SolverAlgorithms.UCS import UCSStrategy
from SolverAlgorithms.AStar import AStarStrategy

#==============================================
# Strategy Factory (Optional - for easy creation)
#==============================================
class StrategyFactory:
    """Factory to create different strategies"""
    
    @staticmethod
    def create_dfs(map_obj, max_depth=50):
        return DFSStrategy(map_obj, max_depth)

    @staticmethod
    def create_bfs(map_obj, max_depth=50):
        return BFSStrategy(map_obj, max_depth)
    
    @staticmethod
    def create_ucs(map_obj, max_depth=50):
        return UCSStrategy(map_obj, max_depth)

    @staticmethod
    def create_astar(map_obj, max_depth=50):   
        return AStarStrategy(map_obj, max_depth)

    @staticmethod
    def get_strategy_names():
        return ['DFS', 'BFS']

    @staticmethod
    def create_strategy_from_name(strategy_name, map_obj, max_depth=50):
        return StrategyFactory.create_strategy(strategy_name, map_obj, max_depth)
    
    @staticmethod
    def create_strategy(strategy_name, map_obj, max_depth=50):
        if strategy_name == 'DFS':
            return DFSStrategy(map_obj, max_depth)
        elif strategy_name == 'BFS':
            return BFSStrategy(map_obj, max_depth)