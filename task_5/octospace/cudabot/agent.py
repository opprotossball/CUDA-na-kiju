# Skeleton for Agent class
import random

def enemy_home(home):
    return 9 if home == 90 else 90

class Agent:
    def __init__(self):
        self.target = None
        self.turn = 0

    def get_action(self, obs: dict) -> dict:
        self.turn += 1
        if self.target is None:
            self.target = enemy_home(obs["planets_occupation"][0][0])
        ship_actions = []
        #ships_sent = 0
        for ship in obs["allied_ships"]:
            # aggro
            if self.turn >= 777:
                direction = 0
                ship_x = ship[1]
                ship_y = ship[2]
                if self.target > ship_x:
                    direction = 0
                elif self.target < ship_x:
                    direction = 2
                elif self.target > ship_y:
                    direction = 1
                else:
                    direction = 3
                ship_id = ship[0]
                move = (ship_id, 0, direction, 3)
                ship_actions.append(move)
            else:
                pass
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
