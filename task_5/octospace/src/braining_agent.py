import random
from cudabot.brain import Brain
from cudabot.state import GameState

class Agent:
    def __init__(self, side):
        self.side = side
        self.brain = Brain(side)
        self.turn = 0
        #self.prev_state = None
        
    def get_action(self, obs: dict) -> dict:
        self.turn += 1
        print(self.turn)

        state = GameState(obs, None, self.side)
        state.return_state()
        print(f"Ships: {len(state.allied_ships)}")
        ship_actions = self.brain.command(state, self.turn,obs)
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