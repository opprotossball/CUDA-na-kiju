import numpy as np


def defensive_agent(friendly_ship, enemy_ships, base_position, is_base_captured, base_hp, side):

    ship_id, x, y, hp, firing_cooldown, move_cooldown = friendly_ship


    #if(): #można strzelić -> strzel OD JANKA!!!!!!!!!!!!!!!!!
        #return

    if(is_base_captured==-1 or (base_hp<50 and is_base_captured==0)): #baza zajmowana -> broń bazy
        return go_to(friendly_ship,base_position)

    if(hp<60): #and no enemies nearby
        return go_to(friendly_ship, base_position)

    if(True): #na spawnie jeśli nie ma wrogów wychodzi trochę od bazy żeby pilnować
        base_x, base_y = base_position
        if(side == 0):
            go_to(friendly_ship,[base_x+5,base_y+5])
        else:
            go_to(friendly_ship,[base_x-5,base_y-5])


 #move = {"action_type":0,"ship_id":0,"direction":2,"speed":1}
def go_to(ship,target_position):
    ship_id, x, y, _, _, _ = ship
    t_x,t_y = target_position
    if(t_x==x and t_y==y):
        return [0,ship_id,0,0]
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