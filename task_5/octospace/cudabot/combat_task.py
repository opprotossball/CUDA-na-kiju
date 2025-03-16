COMBAT_DIST = 7
import numpy as np
from cudabot.state import Ship
import random

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
        if target_direction(enemy_ship, our_ship) is None:
            return (our_ship.ship_id, 0, direction, 1)
    return None

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
                action = combat(ship, attacking_enemy_ship)
                if action is not None:
                    ship_actions.append(action)
        return ship_actions
