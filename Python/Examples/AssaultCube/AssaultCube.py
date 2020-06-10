'''

This is an example usage of pyMemory by reading and writing AssaultCube's memory.
AssaultCube is a free (open source) first person shooter, avaliable at https://assault.cubers.net/

'''

import time
import math

# get the CPlayer, vec3, and euler classes
import acStructs as ac

# memory manager
from pyMemory.pyMemory import *

# create a manager for assaultCube. You can create multiple managers for multiple programs
mem = memory()

# Attach to assault cube, the executable is called "ac_client.exe"
while not mem.attach("ac_client.exe"):
    print("Assault Cube is not open")
    time.sleep(1)
print("Attached to Assault Cube")
attachTime = time.time()

# Get the base address for assaultcube's main module. (this is also called ac_client.exe)
ac_client = mem.getModule("ac_client.exe")

# Main loop
iterations = 0
lastPrintTime = 0
while mem.processRunning(): # while assaultcube is open
    now = time.time()
    tDelta = now - attachTime
    
    # get the address of where localPlayer struct is stored. In assaultcube this is stored offset from the main module by 0x10f4f4 bytes
    lPlayerBase = mem.read(ac_client + 0x10f4f4, type = c.DWORD).value
    
    # read localplayer struct from memory (whose base was just gotten)
    lPlayer = mem.read(lPlayerBase, type = ac.CPlayer)
    currentLookAngles = lPlayer.lookAngles
    currentHealth = lPlayer.health
    
    # roll the screen left and right
    roll = c.float(math.sin(tDelta * 5) * 90)
    
    # write the rolling angle to memory
    mem.write(lPlayerBase + ac.offset['roll'], roll)

    # write 69420 to our health, because thats funny
    mem.write(lPlayerBase + ac.offset['health'], c.int(69420))
    
    # print the average (across the whole program time) iterations per second, every second
    iterations += 1
    if (tDelta - lastPrintTime) > 1:
        print("Iterations per second: %f\t\t\r" % (iterations / tDelta), end = '')
        lastPrintTime = tDelta
