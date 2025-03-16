import numpy as np

class Agent:
    def __init__(self, side):
        self.exploration_targets = []  # List of unexplored areas to target
        self.resource_priority = []  # List of planets with high resource value
        self.enemy_ship_locations = []  # Track enemy ship positions
        self.planet_occupation_priority = []  # Planets to prioritize for colonization
        self.initial_roles_assigned = False  # Flag to track if roles are assigned
        self.home_planet = (0, 0)  # Assume home planet is at (0, 0)
        self.enemy_home_planet = (99, 99)  # Assume enemy home planet is at (99, 99)

    def get_action(self, obs: dict) -> dict:
        """
        Main function to decide actions for the bot based on the current observation.
        """
        game_map = obs["map"]
        allied_ships = obs["allied_ships"]
        enemy_ships = obs["enemy_ships"]
        planets_occupation = obs["planets_occupation"]
        resources = min(obs["resources"])

        # Initialize actions
        ships_actions = []
        construction = 0

        # Step 1: Assign roles to ships at the start of the game
        if not self.initial_roles_assigned:
            self.assign_roles(allied_ships)
            self.initial_roles_assigned = True

        # Step 2: Update exploration targets and resource priorities
        self.update_exploration_targets(game_map)
        self.update_resource_priorities(planets_occupation)

        # Step 3: Assign actions to each ship based on their role
        for ship in allied_ships:
            ship_id, x, y, hp, firing_cooldown, move_cooldown = ship
            role = self.get_ship_role(ship_id)

            # If the ship is on cooldown, skip action
            if move_cooldown > 0 or firing_cooldown > 0:
                continue

            # Priority for all roles: Attack enemy ships on sight
            action = self.attack_enemy_ship(ship, enemy_ships)
            if action:
                ships_actions.append(action)
                continue

            # Role-specific behavior
            if role == "explorer":
                action = self.explore_or_colonize(ship, planets_occupation, game_map)
            elif role == "defender":
                action = self.defend_home_planet(ship, planets_occupation)
            elif role == "attacker":
                action = self.attack_enemy_base(ship)

            if action:
                ships_actions.append(action)

        # Step 4: Build new ships if resources are available
        if resources >= 100:  # Adjust threshold based on resource availability
            construction = 1  # Build 1 ship per turn if resources allow

        return {
            "ships_actions": ships_actions,
            "construction": construction
        }

    def assign_roles(self, allied_ships):
        """
        Assign roles to ships at the start of the game.
        """
        self.ship_roles = {}
        for i, ship in enumerate(allied_ships):
            ship_id = ship[0]
            if i == 0:
                self.ship_roles[ship_id] = "explorer"
            elif i == 1:
                self.ship_roles[ship_id] = "defender"
            elif i == 2:
                self.ship_roles[ship_id] = "attacker"
            else:
                # Default to explorer for additional ships
                self.ship_roles[ship_id] = "explorer"

    def get_ship_role(self, ship_id):
        """
        Get the role of a ship by its ID.
        """
        return self.ship_roles.get(ship_id, "explorer")  # Default to explorer if role not found

    def update_exploration_targets(self, game_map):
        """
        Update the list of unexplored areas to target for exploration.
        """
        self.exploration_targets = []
        for x in range(100):
            for y in range(100):
                if game_map[x][y] == -1:  # Unexplored tile
                    self.exploration_targets.append((x, y))

    def update_resource_priorities(self, planets_occupation):
        """
        Update the list of planets to prioritize based on resource value and occupation status.
        """
        self.resource_priority = []
        for planet in planets_occupation:
            x, y, occupation = planet
            if occupation == -1:  # Unoccupied planet
                self.resource_priority.append((x, y))

    def attack_enemy_ship(self, ship, enemy_ships):
        """
        Attack an enemy ship if it is within firing range.
        """
        ship_id, x, y, _, _, _ = ship
        for enemy in enemy_ships:
            ex, ey = enemy[1], enemy[2]
            distance = abs(ex - x) + abs(ey - y)
            if distance <= 8:  # Enemy is within firing range
                direction = self.get_direction((x, y), (ex, ey))
                return [ship_id, 1, direction, 0]  # Fire at the enemy
        return None

    def explore_or_colonize(self, ship, planets_occupation, game_map):
        """
        Explorer behavior: Colonize unclaimed planets or explore unknown space.
        """
        ship_id, x, y, _, _, _ = ship

        # Priority 1: Colonize unclaimed planets
        for planet in planets_occupation:
            px, py, occupation = planet
            if occupation == -1:  # Unoccupied planet
                distance = abs(px - x) + abs(py - y)
                if distance <= 3:  # Move towards the planet
                    direction = self.get_direction((x, y), (px, py))
                    return [ship_id, 0, direction, 1]  # Move 1 tile towards the planet

        # Priority 2: Explore unknown space
        if self.exploration_targets:
            target = self.exploration_targets.pop(0)  # Get the next exploration target
            direction = self.get_direction((x, y), target)
            return [ship_id, 0, direction, 1]  # Move 1 tile towards the target

        return None

    def defend_home_planet(self, ship, planets_occupation):
        """
        Defender behavior: Protect the home planet.
        """
        ship_id, x, y, _, _, _ = ship
        home_x, home_y = self.home_planet

        # Stay near the home planet
        distance_to_home = abs(home_x - x) + abs(home_y - y)
        if distance_to_home > 3:  # Move closer to the home planet
            direction = self.get_direction((x, y), (home_x, home_y))
            return [ship_id, 0, direction, 1]  # Move 1 tile towards the home planet

        return None

    def attack_enemy_base(self, ship):
        """
        Attacker behavior: Move toward the enemy's home planet.
        """
        ship_id, x, y, _, _, _ = ship
        enemy_x, enemy_y = self.enemy_home_planet

        # Move toward the enemy's home planet
        direction = self.get_direction((x, y), (enemy_x, enemy_y))
        return [ship_id, 0, direction, 1]  # Move 1 tile towards the enemy base

    def get_direction(self, current_pos, target_pos):
        """
        Determine the direction to move from current_pos to target_pos.
        """
        cx, cy = current_pos
        tx, ty = target_pos
        if tx > cx:
            return 0  # Right
        elif tx < cx:
            return 2  # Left
        elif ty > cy:
            return 1  # Down
        else:
            return 3  # Up

    def load(self, abs_path: str):
        """
        Load any necessary weights or models for the agent.
        """
        pass

    def eval(self):
        """
        Switch the agent to inference mode.
        """
        pass

    def to(self, device):
        """
        Move the agent to a GPU for faster computation.
        """
        pass