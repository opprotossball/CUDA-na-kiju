# def is_in_range(ship, target):
#     if player == 0:
#         enemy_ships = player_2_ships
#     else:
#         enemy_ships = player_1_ships

#     if len(enemy_ships.keys()) == 0:
#         return -1

#     ship_vec = np.array([ship_x, ship_y], dtype=int)
#     target_vec = np.array([ship_x, ship_y], dtype=int) + MOVEMENT_DIRECTIONS[direction] * MAX_SHIP_FIRE_RANGE
#     target_vec -= ship_vec
#     vec_to_other_ships = np.array([(x, y) for ship_id, (x, y, hp, firing_cooldown, move_cooldown) in enemy_ships.items()], dtype=int)
#     vec_to_other_ships = vec_to_other_ships - ship_vec
#     vec_angles = [np.arccos(np.clip(np.dot(vec/np.linalg.norm(vec), target_vec/np.linalg.norm(target_vec)), -1.0, 1.0)) if np.linalg.norm(vec) != 0 else 0 for vec in vec_to_other_ships]

#     target_id = -1
#     min_dist = MAX_SHIP_FIRE_RANGE + 1
#     for i in range(len(enemy_ships.keys())):

#         # Get all ships between -15 and 15 degrees
#         if -np.pi/12 <= vec_angles[i] <= np.pi/12 and min_dist > np.linalg.norm(vec_to_other_ships[i]):
#             target_id = list(enemy_ships.keys())[i]
#             min_dist = np.linalg.norm(vec_to_other_ships[i])
#     return target_id

# def combat(our_ship, enemy_ship):
#     pass