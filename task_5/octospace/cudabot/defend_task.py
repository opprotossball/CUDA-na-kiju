LEFT_GUARD_POINTS = [(14, 14), (14, 9), (9, 14)]
RIGHT_GUARD_POINTS = [(85, 85), (85, 90), (90, 85)]

class DefendTask:

    def __init__(self, side):
        self.guard_points = LEFT_GUARD_POINTS if side == 0 else RIGHT_GUARD_POINTS
    
    def command(self, ships, ship_actions):
        for ship in ships:
            point = self.guard_points[ship.ship_id % 3]
            action = ship.go_to(point[0], point[1])
            ship_actions.append(action)
        return ship_actions