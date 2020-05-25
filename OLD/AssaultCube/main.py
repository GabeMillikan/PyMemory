from helper import *
import os
import time
cls = lambda: os.system("cls")

local_player = entity()
entity_list  = entitylist()

while True:
    local_player.set_base(m.read(ac_client + offset['local player'], vartype.int))
    local_player.update()
    entity_list.set_base( m.read(ac_client + offset['entity list'] , vartype.int))
    entity_list.update()
    
    
    for plr in entity_list.players:
        if (not plr.is_real()) or (not plr.is_alive()):
            continue
        if (plr['team'] == local_player['team']):
            continue
        yaw, pitch, roll = plr.get_aimto_angle(local_player['x'], local_player['y'], local_player['z'])
        local_player.set_orientation(yaw, pitch, roll)
        break
        
        
    if local_player['health'] == 100:
        local_player.set_health(69420)