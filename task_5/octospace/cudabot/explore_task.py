
GOOD_SPOTS_TO_CHECK = [[25,75],[50,50],[75,25]]


def find_planet(GameState, ship):

    # # Reset final coordinates
    # final_coords = []

    if GameState.side == 0:
        homebase = (9, 9)
        # Select area around homebase
        homebase_area = []
        for x in range(homebase[0] - 20, homebase[0] + 20): # Safe margin
            for y in range(homebase[1] - 20, homebase[1] + 20):
                homebase_area.append([x, y])
    else:
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
            if planet.occupation == -1:
                planet_coords.append([planet.pos_x, planet.pos_y, 0])
                planet_mode = True
    
    if planet_mode:
        for field in planet_coords:
            x_dist = abs(ship.pos_x - field[0])
            y_dist = abs(ship.pos_y - field[1])
            field.append(x_dist + y_dist)
        closest_field = min(planet_coords, key=lambda field: field[3])
        closest_x, closest_y = closest_field[0], closest_field[1]
    else:
        # Search through the entire game map
        resource_fields = []
        # for y in range(height):
        #     for x in range(width):
        #         tile = GameState.game_map[y, x]
        #         # Skip tiles in homebase area if we're side 0
        #         if GameState.side == 0 and [x, y] in homebase_area:
        #             continue
        #         # Check if tile is not -1
        #         if (tile & 1) == 1 and (tile & 56) != 0 and tile != -1:
        #             resource_fields.append([x, y, tile])
        # Find the closest point among resource fields
        if resource_fields:
            for field in resource_fields:
                x_dist = abs(ship.pos_x - field[0])
                y_dist = abs(ship.pos_y - field[1])
                field.append(x_dist + y_dist)  # Append the distance to each field

            # Find the resource field with minimum distance
            closest_field = max(resource_fields, key=lambda field: field[3])
            
            # Extract x, y coordinates of the closest field
            closest_x, closest_y = closest_field[0], closest_field[1]
        else:
            # Use predefined good spots to explore
            # Use ship ID to distribute ships among different spots
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


    def command(self, state, exploring_ships, ship_actions):
        for ship in exploring_ships:
            coords = find_planet(state, ship)
            action = ship.go_to(coords[0], coords[1])
            ship_actions.append(action)
        return ship_actions
