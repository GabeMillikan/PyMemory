from pyMemory import *

vec3 = c.createStruct(
    c.float, "x",
    c.float, "y",
    c.float, "z",
)

euler = c.createStruct(
    c.float, "yaw",
    c.float, "pitch",
    c.float, "roll",
)

CPlayer = c.createStruct(
	# 0x0
	c.byte, "team", 
	# 0x1
	c.byte * (0x4 - 0x1), "_0x1", 
	# 0x4
	vec3, "headPosition", 
	# 0x10
	vec3, "velocity", 
	# 0x1c
	c.byte * (0x34 - 0x1c), "_0x1c", 
	# 0x34
	vec3, "footPosition", 
	# 0x40
	euler, "lookAngles", 
	# 0x4c
	c.byte * (0xf8 - 0x4c), "_0x4c", 
	# 0xf8
	c.int, "health", 
	# 0xfc
	c.int, "armor", 
	# 0x100
	c.byte * (0x140 - 0x100), "_0xfc", 
	# 0x140
	c.uint, "carbineAmmo", 
	# 0x144
	c.uint, "shotgunAmmo", 
	# 0x148
	c.uint, "submachineAmmo", 
	# 0x14c
	c.uint, "sniperAmmo", 
	# 0x150
	c.uint, "rifleAmmo", 
	# 0x154
	c.byte * (0x1f0 - 0x154), "_0x154", 
	# 0x1f0
	c.uint, "ping", 
	# 0x1f4
	c.byte * (0x1fc - 0x1f4), "_0x1f4", 
	# 0x1fc
	c.uint, "frags", 
	# 0x200
	c.uint, "flags", 
	# 0x204
	c.uint, "deaths", 
	# 0x208
	c.uint, "score", 
	# 0x20c
	c.byte * (0x255 - 0x20c), "_0x20c", 
	# 0x255
	c.char * 260, "name", 
)