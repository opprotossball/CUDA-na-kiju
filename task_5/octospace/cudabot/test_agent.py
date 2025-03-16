import numpy as np
# Skeleton for Agent class
MOVEMENT_DIRECTIONS = np.array([
    [1, 0],
    [0, 1],
    [-1, 0],
    [0, -1]
], dtype=np.int8)

MAX_SHIP_FIRE_RANGE = 8
class Agent:
    def __init__(self, side):
        self.side = side
        self.turn = 0
        
    def get_action(self, obs: dict) -> dict:
        game_map = obs["map"]
        allied_ships = obs["allied_ships"]
        enemy_ships = obs["enemy_ships"]
        planets_occupation = obs["planets_occupation"]
        resources = min(obs["resources"])
        """
        Main function, which gets called during step() of the environment.

        Observation space:
            game_map: whole grid of board_size, which already has applied visibility mask on it
            allied_ships: an array of all currently available ships for the player. The ships are represented as a list:
                (ship id, position x, y, current health points, firing_cooldown, move_cooldown)
                - ship id: int [0, 1000]
                - position x: int [0, 100]
                - position y: int [0, 100]
                - health points: int [1, 100]
                - firing_cooldown: int [0, 10]
                - move_cooldown: int [0, 3]
            enemy_ships: same, but for the opposing player ships
            planets_occupation: for each visible planet, it shows the occupation progress:
                - planet_x: int [0, 100]
                - planet_y: int [0, 100]
                - occupation_progress: int [-1, 100]:
                    -1: planet is unoccupied
                    0: planet occupied by the 1st player
                    100: planet occupied by the 2nd player
                    Values between indicate an ongoing conflict for the ownership of the planet
            resources: current resources available for building

        Action space:
            ships_actions: player can provide an action to be executed by every of his ships.
                The command looks as follows:
                - ship_id: int [0, 1000]
                - action_type: int [0, 1]
                    0 - move
                    1 - fire
                - direction: int [0, 3] - direction of movement or firing
                    0 - right
                    1 - down
                    2 - left
                    3 - up
                - speed (not applicable when firing): int [0, 3] - a number of fields to move
            construction: int [0, 10] - a number of ships to be constructed

        :param obs:
        :return:
        """
        moves=[]
        if (self.side==0):
            base_position=[9,9]
        else:
            base_position = [90, 90]
        is_base_captured=1
        base_hp=100
        for ship in allied_ships:
            move=defensive_agent(ship, enemy_ships, base_position, is_base_captured, base_hp, self.side)
            moves.append(move)
            #print(move)


        return {
            "ships_actions": moves,
            "construction": 1
        }


    def load(self, abs_path: str):
        """
        Function for loading all necessary weights for the agent. The abs_path is a path pointing to the directory,
        where the weights for the agent are stored, so remember to join it to any path while loading.

        :param abs_path:
        :return:
        """
        pass

    def eval(self):
        """
        With this function you should switch the agent to inference mode.

        :return:
        """
        pass

    def to(self, device):
        """
        This function allows you to move the agent to a GPU. Please keep that in mind,
        because it can significantly speed up the computations and let you meet the time requirements.

        :param device:
        :return:
        """
        pass

def defensive_agent(friendly_ship, enemy_ships, base_position, is_base_captured, base_hp, side):

    ship_id, x, y, hp, firing_cooldown, move_cooldown = friendly_ship


    #if(): #można strzelić -> strzel OD JANKA!!!!!!!!!!!!!!!!!
        #return

    if(is_base_captured==-1 or (base_hp<50 and is_base_captured==0)): #baza zajmowana -> broń bazy
        #print("chuj1")
        return go_to(friendly_ship,base_position)

    if(hp<60): #and no enemies nearby
        #print("chuj2")
        return go_to(friendly_ship, base_position)

    if(True): #na spawnie jeśli nie ma wrogów wychodzi trochę od bazy żeby pilnować
        #print("chuj3")
        base_x, base_y = base_position

        if(side == 0):
            return go_to(friendly_ship,[base_x+5,base_y+5])
        else:
            return go_to(friendly_ship,[base_x-5,base_y-5])


 #move = {"action_type":0,"ship_id":0,"direction":2,"speed":1}
def go_to(ship,target_position):
    ship_id, x, y, _, _, _ = ship
    t_x,t_y = target_position
    if(t_x==x and t_y==y):
        return [ship_id,0,0,0]
    ship_id, x, y, _, _, _ = ship
    t_x, t_y = target_position
    ship_x = ship[1]
    ship_y = ship[2]
    if t_x > ship_x:
        direction = 0
    elif t_x < ship_x:
        direction = 2
    elif t_y > ship_y:
        direction = 1
    else:
        direction = 3
    ship_id = ship[0]
    return [ship_id, 0, direction, 3]