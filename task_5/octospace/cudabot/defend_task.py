LEFT_GUARD_POINTS = [(14, 14), (14, 9), (9, 14)]
RIGHT_GUARD_POINTS = [(85, 85), (85, 90), (90, 85)]

class DefendTask:

    def __init__(self, side):
        self.guard_points = LEFT_GUARD_POINTS if side == 0 else RIGHT_GUARD_POINTS
        self.side = side
        self.base_position = [9, 9] if side == 0 else [90, 90]
    
    def command(self, map,state, ships, ship_actions):
        _, _, is_base_captured, base_hp = state.return_state()
        for ship in ships:
            move = defensive_agent(map,ship, self.base_position, self.guard_points[ship.ship_id % 3], is_base_captured, base_hp, self.side)
            ship_actions.append(move)
        return ship_actions

def defensive_agent(map,ship, base_position, guard_position, is_base_captured, base_hp, side):
    if(is_base_captured==-1 or (base_hp<50 and is_base_captured==0)): #baza zajmowana -> broń bazy
        return ship.go_to(map,base_position[0], base_position[1])

    if(ship.hp<60): #and no enemies nearby
        return ship.go_to(map,base_position[0], base_position[1])

    if(True): #na spawnie jeśli nie ma wrogów wychodzi trochę od bazy żeby pilnować
        return ship.go_to(map,guard_position[0], guard_position[1])
