import numpy as np
from state import Ship

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
    if enemy_ship.fire_cooldown != 0 or target_direction(enemy_ship, our_ship) is None:
        return None
    for direction in range(4):
        target_location = np.array([our_ship.pos_x, our_ship.pos_y], dtype=int) + MOVEMENT_DIRECTIONS[direction]
        # move to safe location
        if target_direction(enemy_ship, our_ship) is None:
            return (our_ship.ship_id, 0, target_location, 1)
    # no safe moves - do default
    return (our_ship.ship_id, 0, direction, 3)

if __name__ == "__main__":
    board = np.zeros(shape=(11, 11))
    for i in range(11):
        for j in range(11):
            for d in range(4):
                if is_in_range(Ship.from_tuple((0, 5, 5, 100, 0, 0)), Ship.from_tuple((1, i, j, 100, 0, 0)), d):
                    board[i][j] = 1
    print(board)
