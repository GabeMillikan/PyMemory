from pyMemory import memory
import ctypes as ct
from ctypes import wintypes as wt
import time

mem = memory()

# Attach to assault cube (OpenProcess) 
while not mem.attach("ac_client.exe"):
    print("Assault Cube is not open")
    time.sleep(1)
print("Attached to Assault Cube")

# Get modules
ac_client = mem.getModuleBase("ac_client.exe")
print("ac_client.exe -> %s" % hex(ac_client))

# Get LocalPlayer address
print()
localPlayerBase = mem.read(ac_client + 0x10f4f4, type = wt.DWORD).value
print("LocalPlayer -> %s" % hex(localPlayerBase))

# Periodically print health
print()
while True:
    hp = mem.read(localPlayerBase + 0xf8, type = ct.c_int).value
    print("Current Health: %d\t" % hp, end = '\r')
    time.sleep(1/1000)
