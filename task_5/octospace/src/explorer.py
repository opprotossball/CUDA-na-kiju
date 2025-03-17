class ExplorerAgent:
    def __init__(self):
        self.step = 0
        self.final_coords = []
        self.game_state = None

    def update_game_state(self, game_state):
        """Update the current game state"""
        self.game_state = game_state

    def find_planet(self, GameState):
        self.game_state = GameState

        # Reset final coordinates
        self.final_coords = []

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

        # Check if there are allied ships
        if not GameState.allied_ships:
            return []  # Return empty list if no ships

        for ship in GameState.allied_ships:

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
                for y in range(height):
                    for x in range(width):
                        tile = GameState.game_map[y, x]
                        # Skip tiles in homebase area if we're side 0
                        if GameState.side == 0 and [x, y] in homebase_area:
                            continue
                        # Check if tile is not -1
                        if (tile & 1) == 1 and (tile & 56) != 0 and tile != -1:
                            resource_fields.append([x, y, tile])
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
                    # Simple distribution around map center
                    map_center_x, map_center_y = width // 2, height // 2
                    
                    # Use ship_id to determine direction (one of 4 directions)
                    direction = ship.ship_id % 4
                    offset = 10  # Fixed distance from center
                    
                    if direction == 0:
                        closest_x = map_center_x + offset
                        closest_y = map_center_y
                    elif direction == 1:
                        closest_x = map_center_x
                        closest_y = map_center_y + offset
                    elif direction == 2:
                        closest_x = map_center_x - offset
                        closest_y = map_center_y
                    else:  # direction == 3
                        closest_x = map_center_x
                        closest_y = map_center_y - offset
                    
                    # Ensure coordinates are within map bounds
                    closest_x = min(width - 1, max(0, closest_x))
                    closest_y = min(height - 1, max(0, closest_y))

            self.final_coords.append((closest_x, closest_y))
        
        return self.final_coords


                    
