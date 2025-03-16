class Agent:
    def __init__(self):
        self.exploration_targets = []
        self.resource_priority = []
        self.enemy_ship_locations = []
        self.planet_occupation_priority = []
        self.initial_directions_assigned = False
        self.ship_roles = {}

    def get_action(self, obs: dict) -> dict:
        # Your existing implementation
        pass

    def assign_initial_roles_and_directions(self, allied_ships):
        # Your existing implementation
        pass

    def update_exploration_targets(self, game_map):
        # Your existing implementation
        pass

    def update_resource_priorities(self, planets_occupation):
        # Your existing implementation
        pass

    def heal_ship(self, ship, planets_occupation):
        # Your existing implementation
        pass

    def attack_enemy_ship(self, ship, enemy_ships):
        # Your existing implementation
        pass

    def colonize_or_defend_planet(self, ship, planets_occupation):
        # Your existing implementation
        pass

    def explore_map(self, ship, game_map):
        # Your existing implementation
        pass

    def get_direction(self, current_pos, target_pos):
        # Your existing implementation
        pass

    def load(self, abs_path: str):
        """
        Load a model or weights from the specified path.
        """
        # Example: Load a model using a library like PyTorch or TensorFlow
        try:
            # self.model = torch.load(abs_path)  # Example for PyTorch
            print(f"Model loaded from {abs_path}")
        except Exception as e:
            print(f"Failed to load model: {e}")

    def eval(self):
        """
        Switch the agent to evaluation mode.
        """
        # Example: Set a model to evaluation mode
        # if hasattr(self, 'model'):
        #     self.model.eval()
        print("Agent is in evaluation mode.")

    def to(self, device):
        """
        Move the agent's model to the specified device (e.g., 'cuda' or 'cpu').
        """
        # Example: Move a model to a device
        # if hasattr(self, 'model'):
        #     self.model.to(device)
        print(f"Agent moved to {device}.")