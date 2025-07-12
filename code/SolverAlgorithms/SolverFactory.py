from SolverAlgorithms.DFS import DFSStrategy
from SolverAlgorithms.BFS import BFSStrategy
from SolverAlgorithms.UCS import UCSStrategy
from SolverAlgorithms.AStarr import AStarStrategy

#==============================================
# Strategy Factory (Optional - for easy creation)
#==============================================
class StrategyFactory:
    """Factory to create different strategies"""
    
    @staticmethod
    def create_dfs(map_obj, max_time=30):
        return DFSStrategy(map_obj, max_time)

    @staticmethod
    def create_bfs(map_obj, max_time=30):
        return BFSStrategy(map_obj, max_time)
    
    @staticmethod
    def create_ucs(map_obj, max_time=30):
        return UCSStrategy(map_obj, max_time)

    @staticmethod
    def create_astar(map_obj, max_time=30):   
        return AStarStrategy(map_obj, max_time)

    @staticmethod
    def get_strategy_names():
        return ['DFS', 'BFS', 'UCS', 'A*']

    @staticmethod
    def create_strategy_from_name(strategy_name, map_obj, max_depth=50):
        return StrategyFactory.create_strategy(strategy_name, map_obj, max_depth)
    
    @staticmethod
    def create_strategy(strategy_name, map_obj, max_time=30):
        if strategy_name == 'DFS':
            return DFSStrategy(map_obj, max_time)
        elif strategy_name == 'BFS':
            return BFSStrategy(map_obj, max_time)
        elif strategy_name == 'UCS':
            return UCSStrategy(map_obj, max_time)
        elif strategy_name == 'A*':
            return AStarStrategy(map_obj, max_time)
        else:
            raise ValueError(f"Invalid strategy name: {strategy_name}")