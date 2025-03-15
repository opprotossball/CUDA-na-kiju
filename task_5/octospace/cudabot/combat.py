import numpy as np
from state import Ship

MOVEMENT_DIRECTIONS = np.array([
    [1, 0],
    [0, 1],
    [-1, 0],
    [0, -1]
], dtype=np.int8)
MAX_SHIP_FIRE_RANGE = 8


def is_in_range(ship: Ship, target: Ship, direction):
    enemy_ships = [target]
    ship_vec = np.array([ship.pos_x, ship.pos_y], dtype=int)
    target_vec = np.array([target.pos_x], target.pos_y) + MOVEMENT_DIRECTIONS[direction] * MAX_SHIP_FIRE_RANGE
    target_vec -= ship_vec
    vec_to_other_ships = np.array([(ship.pos_x, ship.pos_y) for ship in enemy_ships], dtype=int)
    vec_to_other_ships = vec_to_other_ships - ship_vec
    vec_angles = [np.arccos(np.clip(np.dot(vec/np.linalg.norm(vec), target_vec/np.linalg.norm(target_vec)), -1.0, 1.0)) if np.linalg.norm(vec) != 0 else 0 for vec in vec_to_other_ships]

    target_id = -1
    min_dist = MAX_SHIP_FIRE_RANGE + 1

        # Get all ships between -15 and 15 degrees
    if -np.pi/12 <= vec_angles[0] <= np.pi/12 and min_dist > np.linalg.norm(vec_to_other_ships[0]):
        return True
        # target_id = i
        # min_dist = np.linalg.norm(vec_to_other_ships[0])
    return False

def combat(our_ship, enemy_ship):
    pass

if __name__ == "__main__":
    board = np.zeros(shape=(11, 11))
    for i in range(11):
        for j in range(11):
            for d in range(4):
                if is_in_range(Ship.from_tuple(0, 5, 5, 100, 0, 0), Ship.from_tuple(1, i, j, 100, 0, 0), d):
                    board[i][j] = 1
    print(board)
