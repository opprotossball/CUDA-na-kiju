### STATE
from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional, Any
import numpy as np
from queue import PriorityQueue

@dataclass
class Ship:
    """
    Class representing a ship in the game
    """
    ship_id: int
    pos_x: int
    pos_y: int
    hp: int
    fire_cooldown: int
    move_cooldown: int

    @classmethod
    def from_tuple(cls, ship_tuple):
        """Create a Ship instance from a tuple representation"""
        return cls(
            ship_id=ship_tuple[0],
            pos_x=ship_tuple[1],
            pos_y=ship_tuple[2],
            hp=ship_tuple[3],
            fire_cooldown=ship_tuple[4],
            move_cooldown=ship_tuple[5]
        )

    def to_tuple(self) -> tuple:
        """Convert ship to tuple representation"""
        return (self.ship_id, self.pos_x, self.pos_y, self.hp,
                self.fire_cooldown, self.move_cooldown)

    def distance_to(self, other_ship) -> float:
        """Calculate distance to another ship"""
        return ((self.pos_x - other_ship.pos_x) ** 2 +
                (self.pos_y - other_ship.pos_y) ** 2) ** 0.5

    def go_to(self, game_map, target_x, target_y, search_size=15):
        origin = (self.pos_x, self.pos_y)
        target = (target_x, target_y)
        if (origin==target):
            return [self.ship_id,0,0,0]
        prev, new_origin, new_target = find_shortest_paths(game_map, origin, target, search_size)
        path = []
        while new_target != new_origin:
            path.append(new_target)
            new_target = prev[new_target]
        next_pos = path[-1]
        direction = 0
        if next_pos[0] > new_origin[0]:
            direction= 0
        elif next_pos[0] < new_origin[0]:
            direction= 2
        elif next_pos[1] > new_origin[1]:
            direction= 1
        else:
            direction= 3
        return [self.ship_id,0,direction,3]


    # origin is a tuple (x, y)
    # game_map is in the original format received from the game engine

    def simple_go_to(self, target_x, target_y):
        direction = 0
        if self.pos_x > target_x:
            direction= 0
        elif self.pos_x < target_x:
            direction= 2
        elif self.pos_y > target_y:
            direction= 1
        elif self.pos_y < target_y:
            direction= 3
        else:
            return [self.ship_id, 0, 0, 0]
        return [self.ship_id,0,direction,3]

@dataclass
class Planet:
    """
    Class representing a planet in the game
    """
    pos_x: int
    pos_y: int
    occupation: int  # -1: unoccupied, 0: player 1, 100: player 2, 1-99: contested

    @classmethod
    def from_tuple(cls, planet_tuple):
        """Create a Planet instance from a tuple representation"""
        return cls(
            pos_x=planet_tuple[0],
            pos_y=planet_tuple[1],
            occupation=planet_tuple[2]
        )

    def to_tuple(self) -> tuple:
        """Convert planet to tuple representation"""
        return (self.pos_x, self.pos_y, self.occupation)

    @property
    def is_contested(self) -> bool:
        """Check if the planet is contested"""
        return 0 < self.occupation < 100

    @property
    def is_friendly(self) -> bool:
        """Check if the planet is controlled by us"""
        return self.occupation == 0

    @property
    def is_enemy(self) -> bool:
        """Check if the planet is controlled by enemy"""
        return self.occupation == 100


class GameState:
    """Class representing the current state of the game

    Example usage:
    state = GameState(obs)
    game_map, current_state, base_status = state.return_state()

    """

    def __init__(self, observation: dict, previous_state=None, side=0):
        """Load the previous game state"""
        self.previous_state = previous_state
        self.side = side

        """Initialize state from observation dictionary"""
        self.game_map = observation.get("map", [])

        # Convert ship tuples to Ship objects
        self.allied_ships = [Ship.from_tuple(ship) for ship in
                             observation.get("allied_ships", [])]
        self.enemy_ships = [Ship.from_tuple(ship) for ship in
                            observation.get("enemy_ships", [])]

        # Convert planet tuples to Planet objects
        self.planets = [Planet.from_tuple(planet) for planet in
                        observation.get("planets_occupation", [])]

        self.resources = observation.get("resources", 0)

        self.updating_map = []
        for x in range(len(self.game_map)):
            self.updating_map.append([])
            for y in range(len(self.game_map[x])):
                # Skip unobserved tiles
                if self.game_map[x][y] == -1:
                    self.updating_map[x].append(-1)
                    continue

                # Copy the original bit value to maintain all encoded properties
                self.updating_map[x].append(self.game_map[x][y])

    def return_state(self):
        current_state = {
            "game_map": self.game_map,
            "allied_ships": [ship.to_tuple() for ship in self.allied_ships],
            "enemy_ships": [ship.to_tuple() for ship in self.enemy_ships],
            "planets_occupation": [planet.to_tuple() for planet in self.planets],
            "resources": self.resources
        }
        base_status = 1  # 1: base is 100% hp, -1: base was just attacked, 0: base is less than 100% hp, but the hp didn't change
        current_base_hp = 100
        if self.previous_state is not None:
            for planet in self.previous_state["planets_occupation"]:
                base_coords = 9 if self.side == 0 else 90
                if self.side == 0:
                    current_base_hp = 100 - current_state["planets_occupation"][0][2]
                    previous_base_hp = 100 - planet[2]
                else:
                    current_base_hp = current_state["planets_occupation"][0][2]
                    previous_base_hp = planet[2]
                if planet[0] == base_coords and planet[1] == base_coords:
                    if previous_base_hp - current_base_hp > 0:
                        base_status = -1
                    elif current_base_hp < 100:
                        base_status = 0
        return self.updating_map, current_state, base_status, current_base_hp


def find_shortest_paths(game_map, origin, target, search_size):
    cut_game_map, origin, target, rect = cut_search_area(game_map, origin, search_size, target)
    nodes = PriorityQueue()
    prev = np.empty(np.shape(cut_game_map), dtype=tuple)
    dist = np.zeros(np.shape(cut_game_map))
    removed = []
    for i in range(len(cut_game_map)):
        for j in range(len(cut_game_map[i])):
            nodes.put((float('inf'), (i, j)))
            dist[i, j] = float('inf')
    nodes.put((0, origin))
    dist[origin] = 0
    while not len(removed) == len(cut_game_map) * len(cut_game_map[0]):
        weight, node = nodes.get()
        if node in removed:
            continue
        removed.append(node)
        x, y = node
        for neigh in get_neighbors(node, cut_game_map):
            if neigh not in removed:
                alt = dist[x, y] + calc_weight(game_map, (x + rect[0][0], y + rect[0][1]), 3)
                if alt < dist[neigh]:
                    dist[neigh] = alt
                    prev[neigh] = node
                    nodes.put((alt, neigh))
        # if node == target:
        #     break

    return prev, origin, target


def get_neighbors(point, game_map):
    x, y = point
    neighbors = []
    for i in range(-1, 2):
        for j in range(-1, 2):
            if i == 0 and j == 0:
                continue
            if x + i < 0 or x + i >= len(game_map) or y + j < 0 or y + j >= len(game_map[0]):
                continue
            neighbors.append((x + i, y + j))
    return neighbors


def calc_weight(game_map, node, def_weight):
    x, y = node
    if game_map[y, x] & int('00000010', 2):  # asteroids
        return def_weight + 5
    elif game_map[y, x] & int('00000100', 2):  # boost field
        return 0
    return def_weight
    # origin is a tuple (x, y)
    # game_map is in the original format received from the game engine


def cut_search_area(game_map, origin, search_size, target):
    coords = [[origin[0], origin[1]], [target[0], target[1]]]  # left top corner, right bottom corner
    coords[0][0] = min(origin[0], target[0])
    coords[0][1] = min(origin[1], target[1])
    coords[1][0] = max(origin[0], target[0])
    coords[1][1] = max(origin[1], target[1])
    if coords[1][0] - coords[0][0] > search_size:
        if origin[0] < target[0]:
            coords[1][0] = origin[0] + search_size
        else:
            coords[0][0] = origin[0] - search_size
    if coords[1][1] - coords[0][1] > search_size:
        if origin[1] < target[1]:
            coords[1][1] = origin[1] + search_size
        else:
            coords[0][1] = origin[1] - search_size
    game_map = game_map[coords[0][0]:coords[1][0] + 1, coords[0][1]:coords[1][1] + 1]
    new_origin = (origin[0] - coords[0][0], origin[1] - coords[0][1])
    new_target = (target[0] - coords[0][0], target[1] - coords[0][1])
    if origin[0] <= target[0] and origin[1] <= target[1]:
        new_target = (coords[1][0] - coords[0][0], coords[1][1] - coords[0][1])
    elif origin[0] <= target[0] and origin[1] >= target[1]:
        new_target = (coords[1][0] - coords[0][0], 0)
    elif origin[0] >= target[0] and origin[1] <= target[1]:
        new_target = (0, coords[1][1] - coords[0][1])
    elif origin[0] >= target[0] and origin[1] >= target[1]:
        new_target = (0, 0)
    return game_map, new_origin, new_target, coords

### TASKS

LEFT_GUARD_POINTS = [(14, 14), (14, 9), (9, 14)]
RIGHT_GUARD_POINTS = [(85, 85), (85, 90), (90, 85)]

class DefendTask:

    def __init__(self, side):
        self.guard_points = LEFT_GUARD_POINTS if side == 0 else RIGHT_GUARD_POINTS
        self.side = side
        self.base_position = [9, 9] if side == 0 else [90, 90]
    
    def command(self, map,state, ships, ship_actions):
        _, _, is_base_captured, base_hp = state.return_state()
        for ship in ships:
            move = defensive_agent(map,ship, self.base_position, self.guard_points[ship.ship_id % 3], is_base_captured, base_hp, self.side)
            ship_actions.append(move)
        return ship_actions

def defensive_agent(map,ship, base_position, guard_position, is_base_captured, base_hp, side):
    print(f"base h: {base_hp}")
    if(base_hp<50): #baza zajmowana -> broń bazy
        return ship.go_to(map,base_position[0], base_position[1])

    if(ship.hp<60): #and no enemies nearby
        return ship.go_to(map,base_position[0], base_position[1])

    if(True): #na spawnie jeśli nie ma wrogów wychodzi trochę od bazy żeby pilnować
        return ship.go_to(map,base_position[0], base_position[1])

COMBAT_DIST = 9
MOVEMENT_DIRECTIONS = np.array([
    [1, 0],
    [0, 1],
    [-1, 0],
    [0, -1]
], dtype=np.int8)
MAX_SHIP_FIRE_RANGE = 8

def target_direction(ship: Ship, target: Ship):
    for direction in range(4):
        enemy_ships = [target]
        ship_vec = np.array([ship.pos_x, ship.pos_y], dtype=int)
        target_vec = np.array([target.pos_x, target.pos_y]) + MOVEMENT_DIRECTIONS[direction] * MAX_SHIP_FIRE_RANGE
        target_vec -= ship_vec
        vec_to_other_ships = np.array([(ship.pos_x, ship.pos_y) for ship in enemy_ships], dtype=int)
        vec_to_other_ships = vec_to_other_ships - ship_vec
        vec_angles = [np.arccos(np.clip(np.dot(vec/np.linalg.norm(vec), target_vec/np.linalg.norm(target_vec)), -1.0, 1.0)) if np.linalg.norm(vec) != 0 else 0 for vec in vec_to_other_ships]
        min_dist = MAX_SHIP_FIRE_RANGE + 1

        # Get all ships between -15 and 15 degrees
        if -np.pi/12 <= vec_angles[0] <= np.pi/12 and min_dist > np.linalg.norm(vec_to_other_ships[0]):
            return direction
    return None

def combat(our_ship: Ship, enemy_ship: Ship):
    if our_ship.fire_cooldown == 0:
        direction = target_direction(our_ship, enemy_ship)
        if direction is not None:
            # shoot enemy
            return (our_ship.ship_id, 1, direction)
    # do nothing if safe
    if enemy_ship.fire_cooldown != 0:
        return (our_ship.ship_id, 0, random.randint(0, 3), 1)
    for direction in range(4):
        target_location = np.array([our_ship.pos_x, our_ship.pos_y], dtype=int) + MOVEMENT_DIRECTIONS[direction]
        # move to safe location
        fake_ship = Ship.from_tuple((999, target_location[0], target_location[1], 100, 0, 0))
        if target_direction(enemy_ship, fake_ship) is None:
            return (our_ship.ship_id, 0, direction, 1)
    return None

def aggressive_combat(our_ship: Ship, enemy_ship: Ship):
    if our_ship.fire_cooldown == 0:
        direction = target_direction(our_ship, enemy_ship)
        if direction is not None:
            # shoot enemy
            return (our_ship.ship_id, 1, direction)
        else:
            return our_ship.simple_go_to(enemy_ship.pos_x, enemy_ship.pos_y)
    # dodge
    if enemy_ship.fire_cooldown == 0:
        for direction in range(4):
            target_location = np.array([our_ship.pos_x, our_ship.pos_y], dtype=int) + MOVEMENT_DIRECTIONS[direction]
            # move to safe location
            fake_ship = Ship.from_tuple((999, target_location[0], target_location[1], 100, 0, 0))
            if target_direction(enemy_ship, fake_ship) is None:
                return (our_ship.ship_id, 0, direction, 1)

    return our_ship.simple_go_to(enemy_ship.pos_x, enemy_ship.pos_y)

class CombatTask:

    def __init__(self, side):
        pass

    def command(self, state, ships, ship_actions):
        for ship in ships:
            attacking_enemy_ship = None
            for enemy_ship in state.enemy_ships:
                dist = ship.distance_to(enemy_ship)
                if dist <= COMBAT_DIST:
                    attacking_enemy_ship = enemy_ship
            if attacking_enemy_ship is not None:
                action = aggressive_combat(ship, attacking_enemy_ship)
                if action is not None:
                    ship_actions.append(action)
        return ship_actions

LEFT_BASE = [90,90]
RIGHT_BASE = [9,9]

class ConquerTask:

    def __init__(self, side):
        self.target = RIGHT_BASE if side == 1 else LEFT_BASE

    def command(self, map, ships, ship_actions):
        for ship in ships:
            action = ship.go_to(map,self.target[0], self.target[1])
            ship_actions.append(action)
        return ship_actions

GOOD_SPOTS_TO_CHECK = [[25,75],[50,50],[75,25]]

resource_cache = None
checked_spots = None

def find_planet(GameState, ship):
    global resource_cache
    occupation_value = 0
    # # Reset final coordinates
    # final_coords = []

    if GameState.side == 0:
        ocupation_value = 0 # value for checking planets
        homebase = (9, 9)
        # Select area around homebase
        homebase_area = []
        for x in range(homebase[0] - 20, homebase[0] + 20): # Safe margin
            for y in range(homebase[1] - 20, homebase[1] + 20):
                homebase_area.append([x, y])
    else:
        occupation_value = 100
        homebase = (90, 90)
        # Select area around homebase
        homebase_area = []
        for x in range(homebase[0] - 20, homebase[0] + 20):
            for y in range(homebase[1] - 20, homebase[1] + 20):
                homebase_area.append
                homebase_area.append([x, y])


    height, width = GameState.game_map.shape

    # Search planets
    planet_mode = False
    planet_coords = []
    if GameState.planets:
        for planet in GameState.planets:
            if planet.occupation != occupation_value and planet.pos_x != homebase[0] and planet.pos_y != homebase[1]:
                planet_coords.append([int(planet.pos_x), int(planet.pos_y)])
                planet_mode = True
    
    if planet_mode:
        for field in planet_coords:
            x_dist = abs(ship.pos_x - field[0])
            y_dist = abs(ship.pos_y - field[1])
            field.append(x_dist + y_dist)
        closest_field = min(planet_coords, key=lambda field: field[2])
        closest_y, closest_x = closest_field[0], closest_field[1]
    else:
        # Search through the entire game map
        if resource_cache is None:
            resource_cache = []
            for y in range(height):
                for x in range(width):
                    tile = GameState.game_map[y, x]
                    # Skip tiles in homebase area if we're side 0
                    if GameState.side == 0 and [x, y] in homebase_area:
                        continue
                    # Check if tile is not -1
                    if (tile & 1) == 1 and (tile & 56) != 0 and tile != -1:
                        resource_cache.append([x, y, tile])
        # Find the closest point among resource fields
        if resource_cache:
            for field in resource_cache:
                x_dist = abs(ship.pos_x - field[0])
                y_dist = abs(ship.pos_y - field[1])
                field.append(x_dist + y_dist)  # Append the distance to each field

            # Find the resource field with minimum distance
            closest_field = max(resource_cache, key=lambda field: field[3])
            
            # Extract x, y coordinates of the closest field
            closest_y, closest_x = closest_field[0], closest_field[1]
        else:
            # Use predefined good spots to explore
            # Use ship ID to distribute ships among different spots
            unknown_tiles = []
            for y in range(height):
                for x in range(width):
                    if GameState.game_map[y, x] == -1:
                        unknown_tiles.append((x, y))
            if unknown_tiles:
                furthest_tile = min(unknown_tiles, key=lambda coord: abs(ship.pos_x - coord[0]) + abs(ship.pos_y - coord[1]))
                closest_x, closest_y = furthest_tile
            else:
                # Fallback to predefined spots if no unknown tiles exist
                spot_index = ship.ship_id % len(GOOD_SPOTS_TO_CHECK)
                closest_x, closest_y = GOOD_SPOTS_TO_CHECK[spot_index]
            
            # Ensure coordinates are within map bounds
            closest_x = min(width - 1, max(0, closest_x))
            closest_y = min(height - 1, max(0, closest_y))

    final_coords = (closest_x, closest_y)
    
    return final_coords

class ExploreTask:
    def __init__(self, side):
        self.side = side
        self.step = 0
        self.final_coords = []
        self.game_state = None

    def command(self, map, state, exploring_ships, ship_actions):
        for ship in exploring_ships:
            coords = find_planet(state, ship)
            action = ship.go_to(map, coords[0], coords[1])
            ship_actions.append(action)
        return ship_actions

### BRAIN

class Brain:
    DOOMSDAY = 1700
    COMBAT_DIST = 7

    def __init__(self, side):
        self.defender = DefendTask(side)
        self.fighter = CombatTask(side)
        self.conquer = ConquerTask(side)
        self.explore = ExploreTask(side)
        self.exploring_ship = None
        self.side = side

    def command(self, state, turn, obs):

        combating_ships = []
        defending_ships = []
        conquering_ships = []
        exploring_ships = []

        ship_ids = []
        for ship in state.allied_ships:
            ship_ids.append(ship.ship_id)

        for ship in state.allied_ships:
            # check for combats 
            attacked = False
            for enemy_ship in state.enemy_ships:
                dist = ship.distance_to(enemy_ship)
                if dist <= Brain.COMBAT_DIST:
                    attacked = True
            if attacked:
                if (turn >= Brain.DOOMSDAY and ship.fire_cooldown>0):
                    conquering_ships.append(ship)
                else:
                    combating_ships.append(ship)
            elif self.exploring_ship is None or self.exploring_ship == ship.ship_id or self.exploring_ship not in ship_ids:
                self.exploring_ship = ship.ship_id
                exploring_ships.append(ship) 
            elif turn >= Brain.DOOMSDAY: #and ship.ship_id % 2==0:
                conquering_ships.append(ship)
            else:
                defending_ships.append(ship)
        map = obs["map"]
        ship_actions = []
        self.defender.command(map,state, defending_ships, ship_actions)
        self.fighter.command(state, combating_ships, ship_actions)
        self.conquer.command(map,conquering_ships, ship_actions)
        self.explore.command(map, state, exploring_ships, ship_actions)
        return ship_actions


class Agent:
    def __init__(self, side):
        self.side = side
        self.brain = Brain(side)
        self.turn = 0
        #self.prev_state = None
        
    def get_action(self, obs: dict) -> dict:
        self.turn += 1

        state = GameState(obs, None, self.side)
        state.return_state()
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
