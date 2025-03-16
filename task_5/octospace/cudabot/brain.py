from cudabot.state import Ship, GameState
from cudabot.defend_task import DefendTask
from cudabot.conquer_task import ConquerTask
from cudabot.combat_task import CombatTask
from cudabot.explore_task import ExploreTask
from cudabot.exterminate_task import ExterminateTask

class Brain:
    DOOMSDAY = 100
    COMBAT_DIST = 7

    def __init__(self, side):
        self.defender = DefendTask(side)
        self.fighter = CombatTask(side)
        self.exterminator = ExterminateTask(side)
        self.conquer = ConquerTask(side)
        self.explore = ExploreTask(side)

    def command(self, state, turn):

        combating_ships = []
        defending_ships = []
        attacking_ships = []
        conquering_ships = []
        exploring_ships = []

        for ship in state.allied_ships:
            # check for combats 
            attacked = False
            for enemy_ship in state.enemy_ships:
                dist = ship.distance_to(enemy_ship)
                if dist <= Brain.COMBAT_DIST:
                    attacked = True
            if attacked:
                if (turn >= Brain.DOOMSDAY and """ship.ship_id % 2 == 0 """and ship.fire_cooldown>0):
                    conquering_ships.append(ship)
                else:
                    combating_ships.append(ship)
            elif turn >= Brain.DOOMSDAY and ship.ship_id % 3==0:
                if (ship.ship_id % 2 == 0 and ship.fire_cooldown):
                    conquering_ships.append(ship)
                else:
                    attacking_ships.append(ship)
            else:
                if(False):
                    exploring_ships.append(ship) # TODO!!!!!!!
                else:
                    defending_ships.append(ship)

        ship_actions = []
        self.defender.command(state, defending_ships, ship_actions)
        self.fighter.command(state, combating_ships, ship_actions)
        self.exterminator.command(attacking_ships, ship_actions)
        self.conquer.command(conquering_ships, ship_actions)
        self.explore.command(exploring_ships, ship_actions)
        return ship_actions
    