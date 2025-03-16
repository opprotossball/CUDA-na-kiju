LEFT_GUARD_POINTS = [(14, 14), (14, 9), (9, 14)]
RIGHT_GUARD_POINTS = [(85, 85), (85, 90), (90, 85)]

class DefendTask:

    def __init__(self, side):
        self.guard_points = LEFT_GUARD_POINTS if side == 0 else RIGHT_GUARD_POINTS
        self.side = side
        self.base_position = [9,9] if side == 0 else [90,90]
    
    def command(self, ships, ship_actions):
        for ship in ships:
            move = defensive_agent(ship, self.base_position, is_base_captured, base_hp, self.side)
            ship_actions.append(move)
        return ship_actions

def defensive_agent(ship, base_position, is_base_captured, base_hp, side):

    ship_id, x, y, hp, firing_cooldown, move_cooldown = ship

    if(is_base_captured==-1 or (base_hp<50 and is_base_captured==0)): #baza zajmowana -> broń bazy
        #print("chuj1")
        return ship.go_to(ship,base_position)

    if(hp<60): #and no enemies nearby
        #print("chuj2")
        return ship.go_to(ship, base_position)

    if(True): #na spawnie jeśli nie ma wrogów wychodzi trochę od bazy żeby pilnować
        #print("chuj3")
        base_x, base_y = base_position

        if(side == 0):
            return ship.go_to(ship,[base_x+5,base_y+5])
        else:
            return ship.go_to(ship,[base_x-5,base_y-5])