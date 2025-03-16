from cudabot.state import Ship, GameState
from cudabot.defend_task import DefendTask
from cudabot.combat_task import CombatTask
from cudabot.exterminate_task import ExterminateTask

class Brain:
    DOOMSDAY = 600
    COMBAT_DIST = 7

    def __init__(self, side):
        self.defender = DefendTask(side)
        self.fighter = CombatTask(side)
        self.exterminator = ExterminateTask(side)

    def command(self, state, turn):

        combating_ships = []
        defending_ships = []
        attacking_ships = []

        for ship in state.allied_ships:
            # check for combats 
            attacked = False
            for enemy_ship in state.enemy_ships:
                dist = ship.distance_to(enemy_ship)
                if dist <= Brain.COMBAT_DIST:
                    attacked = True
            if attacked:
                combating_ships.append(ship)
            elif turn >= Brain.DOOMSDAY and ship.ship_id < 3:
                attacking_ships.append(ship)
            else:
                defending_ships.append(ship)

        ship_actions = []
        self.defender.command(defending_ships, ship_actions)
        self.fighter.command(state, combating_ships, ship_actions)
        self.exterminator.command(attacking_ships, ship_actions)
        return ship_actions
    