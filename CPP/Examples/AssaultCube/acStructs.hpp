#pragma once

// relevant offsets used in this demo
namespace offset {
	unsigned int roll = 0x48;
	unsigned int health = 0xf8;
}

struct vec3
{
	float x, y, z;
};

struct euler
{
	float yaw, pitch, roll;
};


class CPlayer
{
public:
	// 0x0
	char team;
	// 0x1
	char _0x1[0x4 - 0x1];
	// 0x4
	vec3 headPosition;
	// 0x10
	vec3 velocity;
	// 0x1c
	char _0x1c[0x34 - 0x1c];
	// 0x34
	vec3 footPosition;
	// 0x40
	euler lookAngles;
	// 0x4c
	char _0x4c[0xf8 - 0x4c];
	// 0xf8
	int32_t health;
	// 0xfc
	int32_t armor;
	// 0x100
	char _0xfc[0x140 - 0x100];
	// 0x140
	uint32_t carbineAmmo;
	// 0x144
	uint32_t shotgunAmmo;
	// 0x148
	uint32_t submachineAmmo;
	// 0x14c
	uint32_t sniperAmmo;
	// 0x150
	uint32_t rifleAmmo;
	// 0x154
	char _0x154[0x1f0 - 0x154];
	// 0x1f0
	uint32_t ping;
	// 0x1f4
	char _0x1f4[0x1fc - 0x1f4];
	// 0x1fc
	uint32_t frags;
	// 0x200
	uint32_t flags;
	// 0x204
	uint32_t deaths;
	// 0x208
	uint32_t score;
	// 0x20c
	char _0x20c[0x255 - 0x20c];
	// 0x255
	char name[260];
};
