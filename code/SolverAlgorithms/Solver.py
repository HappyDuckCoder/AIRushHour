from constants import *
from abc import ABC, abstractmethod

class SolverStrategy(ABC):
    
    @abstractmethod
    def solve(self, map_obj):
        pass
    
    @abstractmethod
    def get_name(self):
        pass

class BaseSolver:

    def __init__(self, map_obj):
        self.map = map_obj

    def solve(self):
        pass


class PuzzleSolver:
    def __init__(self, map_obj, strategy: SolverStrategy = None):
        self.map = map_obj
        self.strategy = strategy
    
    def set_strategy(self, strategy: SolverStrategy):
        self.strategy = strategy
    
    def solve(self):
        print(f"Using strategy: {self.strategy.get_name()}")
        return self.strategy.solve()
    
    def get_strategy_name(self):
        return self.strategy.get_name()