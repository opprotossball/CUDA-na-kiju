# Skeleton for Agent class
import random
from src.state import Ship

def enemy_home(home):
    return 9 if home == 90 else 90

class Agent:
    def __init__(self, side):
        self.side = side
        self.target = None
        
    def get_action(self, obs: dict) -> dict:
        map = obs["map"]
        if self.target is None:
            self.target = enemy_home(obs["planets_occupation"][0][0])
        ship_actions = []
        for raw_ship in obs["allied_ships"]:
            ship = Ship.from_tuple(raw_ship)
            print(f"Target: {self.target, self.target}")
            print(f"Ship move: {ship.go_to(map, self.target, self.target)}")
            ship_actions.append(ship.go_to(map,self.target, self.target))
        return {
            "ships_actions": ship_actions,
            "construction": 10
        }
    
    def load(self, abs_path: str):
        pass

    def eval(self):
        pass

    def to(self, device):
        pass