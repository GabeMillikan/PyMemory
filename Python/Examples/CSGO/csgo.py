# imports 
import time, math
from pyMemory.pyMemory import *
from hazedumper.hazedumper import offsets
sigs = offsets['signatures']
netvars = offsets['netvars']

# constants & structs
VK_RETURN = 0x0D
VK_SPACE  = 0x20
VK_U      = 0x55
VK_Y      = 0x59

glowStruct = c.createStruct(
    c.char*4, 'base',
	c.float, 'red',
	c.float, 'green',
	c.float, 'blue',
	c.float, 'alpha',
	c.char*16, '_0x14',
	c.bool, 'renderWhenOccluded',
	c.bool, 'renderWhenUnOccluded',
	c.bool, 'fullBloom',
	c.char*5, '_0x17',
	c.int, 'glowStyle',
)

# load memory
mem = memory()
if not mem.attach("csgo.exe"):
    print("CS:GO is not running, waiting for it to start")
    while not mem.attach("csgo.exe"):
        time.sleep(1)
print("CS:GO attached")

modules = {
    "client": mem.getModule("client.dll"),
    "engine": mem.getModule("engine.dll"),
}
print("Got modules")

# get offsets
localPlayer = mem.read(modules['client'] + sigs['dwLocalPlayer'], c.dword).value
while not localPlayer:
    localPlayer = mem.read(modules['client'] + sigs['dwLocalPlayer'], c.dword).value
print("Got addresses")

# main loop
s = time.time()
i = 0
iterationsPerSecond = 100
chatIsOpen = False
while mem.processRunning():
    if GetAsyncKeyState(VK_U) or GetAsyncKeyState(VK_Y): chatIsOpen = True; # pressing u or y opens chat
    if GetAsyncKeyState(VK_RETURN): chatIsOpen = False; # pressing enter closes chat
    
    if (not chatIsOpen) and GetAsyncKeyState(VK_SPACE): # if pressing spacebar, bunnyhop
        fFlags = mem.read(localPlayer + netvars['m_fFlags'], c.int).value
        isOnGround = (fFlags & (1 << 0)) or (fFlags & (1 << 18))
        if isOnGround:
            mem.write(modules['client'] + sigs['dwForceJump'], c.int(6))

    if False: # wallhacks
        glowObjectAddr = mem.read(modules['client'] + sigs['dwGlowObjectManager'], c.dword).value
        for entityIndex in range(64):
            entityBase = mem.read(modules['client'] + sigs['dwEntityList'] + entityIndex * 0x10, c.dword).value
            if (not entityBase):
                continue
            
            glowIndex = mem.read(entityBase + netvars['m_iGlowIndex'], c.int).value
            ogGlow = mem.read(glowObjectAddr + glowIndex * 0x38, glowStruct)
            ogGlow.blue = 1
            ogGlow.alpha = 1
            ogGlow.renderWhenOccluded = True
            ogGlow.renderWhenUnOccluded = False
            mem.write(glowObjectAddr + glowIndex * 0x38, ogGlow)
    
    # track working fps
    i+=1
    if i % int(iterationsPerSecond/2) == 0:
        now = time.time()
        iterationsPerSecond = i/(now-s)
        print("Iterations per second: %d" % iterationsPerSecond, end = "\t\t\r")
        i = 0
        s = now