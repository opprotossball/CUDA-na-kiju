# Skeleton for Agent class
import random
import numpy as np
from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional, Any

MOVEMENT_DIRECTIONS = np.array([
    [1, 0],
    [0, 1],
    [-1, 0],
    [0, -1]
], dtype=np.int8)
MAX_SHIP_FIRE_RANGE = 8

DOOMSDAY = 777
COMBAT_DIST = 10


### STATE
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
        return (self.pos_x, self.pos_y, self.occupation)
    
    @property
    def is_contested(self) -> bool:
        return 0 < self.occupation < 100
    
    @property
    def is_friendly(self) -> bool:
        return self.occupation == 0
    
    @property
    def is_enemy(self) -> bool:
        return self.occupation == 100


class GameState:
    def __init__(self, observation: dict, previous_state=None):
        self.previous_state = previous_state

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
        is_base_attacked = False
        if self.previous_state is not None:
            for planet in self.previous_state["planets_occupation"]:
                if planet[0] == 90 and planet[1] == 90:
                    if planet[2] - current_state["planets_occupation"][0][2] > 0:
                        is_base_attacked = True
        return self.updating_map, current_state, is_base_attacked
    
def enemy_home(home):
    return 9 if home == 90 else 90

class Agent:
    def __init__(self, side: int):
        self.side = side
        self.target = None
        self.turn = 0

    def get_action(self, obs: dict) -> dict:
        self.turn += 1
        if self.target is None:
            self.target = enemy_home(obs["planets_occupation"][0][0])
        ship_actions = []
        #ships_sent = 0
        for ship in obs["allied_ships"]:
            # COMBAT
            attacking_enemy_ship = None
            for enemy_ship in obs["enemy_ships"]:
                dist = Ship.from_tuple(ship).distance_to(Ship.from_tuple(enemy_ship))
                if dist <= COMBAT_DIST:
                    attacking_enemy_ship = Ship.from_tuple(enemy_ship)
            if attacking_enemy_ship is not None:
                print("ENTERING COMBAT! DIE!!!")
                action = combat(Ship.from_tuple(ship), attacking_enemy_ship)
                if action is not None:
                    ship_actions.append(action)
            # EXTERMINATE 
            elif self.turn >= DOOMSDAY:
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

def target_direction(ship: Ship, target: Ship):
    for direction in range(4):
        enemy_ships = [target]
        ship_vec = np.array([ship.pos_x, ship.pos_y], dtype=int)
        target_vec = MOVEMENT_DIRECTIONS[direction] * MAX_SHIP_FIRE_RANGE
        # target_vec -= ship_vec
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
        print(f"target direction: {direction}")
        if direction is not None:
            # shoot enemy
            return (our_ship.ship_id, 1, direction)
    # do random thing if safe
    if enemy_ship.fire_cooldown != 0 or target_direction(enemy_ship, our_ship) is None:
        return (our_ship.ship_id, 0, random.randint(0, 3), 3)
    for direction in range(4):
        target_location = np.array([our_ship.pos_x, our_ship.pos_y], dtype=int) + MOVEMENT_DIRECTIONS[direction]
        # move to safe location
        if target_direction(enemy_ship, our_ship) is None:
            return (our_ship.ship_id, 0, target_location, 1)
    # no safe moves - do default
    return (our_ship.ship_id, 0, random.randint(0, 3), 3)

