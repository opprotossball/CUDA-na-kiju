LEFT_BASE = [90,90]
RIGHT_BASE = [9,9]

class ConquerTask:

    def __init__(self, side):
        self.target = RIGHT_BASE if side == 1 else LEFT_BASE

    def command(self, ships, ship_actions):
        for ship in ships:
            print("CONQUERING!")
            action = ship.go_to(self.target[0], self.target[1])
            ship_actions.append(action)
        return ship_actions
