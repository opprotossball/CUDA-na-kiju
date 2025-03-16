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

                if planet[0] == base_coords and planet[1] == base_coords:
                    current_base_hp = current_state["planets_occupation"][0][2]
                    previous_base_hp = planet[2]
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
    print(coords)
    print(new_origin)
    print(new_target)
    return game_map, new_origin, new_target, coords