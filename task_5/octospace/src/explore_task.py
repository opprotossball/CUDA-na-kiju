
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
                print(f"Planet coords: {planet.pos_x}, {planet.pos_y}")
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
            print(f"Closest field: {closest_x}, {closest_y}")
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

    # def update_game_state(self, game_state):
    #     """Update the current game state"""
    #     self.game_state = game_state


    def command(self, map, state, exploring_ships, ship_actions):
        for ship in exploring_ships:
            coords = find_planet(state, ship)
            action = ship.go_to(map, coords[0], coords[1])
            ship_actions.append(action)
        return ship_actions
