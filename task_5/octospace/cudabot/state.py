from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional, Any

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
    
    def go_to(self, target_x, target_y):
        if target_x > self.pos_x:
            direction = 0
        elif target_x < self.pos_x:
            direction = 2
        elif target_y > self.pos_y:
            direction = 1
        elif target_y < self.pos_y:
            direction = 3
        else:
            # stay in place
            return (self.ship_id, 0, 0, 0)
        return (self.ship_id, 0, direction, 3)

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
        base_status = 1 # 1: base is 100% hp, -1: base was just attacked, 0: base is less than 100% hp, but the hp didn't change
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