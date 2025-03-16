class ExterminateTask:

    def __init__(self, side):
        self.target = 90 if side == 0 else 9
    
    def command(self, ships, ship_actions):
        for ship in ships:
            action = ship.go_to(self.target, self.target)
            ship_actions.append(action)
        return ship_actions
    