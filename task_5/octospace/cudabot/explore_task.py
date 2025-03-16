GOOD_SPOTS_TO_CHECK = [[25,75],[50,50],[75,25]]
class ExploreTask:

    def __init__(self, side):
        pass

    def command(self, ships, ship_actions):

        for ship in ships:
            self.target = GOOD_SPOTS_TO_CHECK[ship.ship_id%3]    # TODO!!!!!!! (Cała klasa i algorytm od Mikołaja )
            action = ship.go_to(self.target[0], self.target[1])
            ship_actions.append(action)
        return ship_actions
