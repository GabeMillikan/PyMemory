/*

This is an example usage of pyMemory by reading and writing AssaultCube's memory.
AssaultCube is a free (open source) first person shooter, avaliable at https://assault.cubers.net/

Except this is written in c++

*/

#include <iostream>
#include <chrono>
#include <thread>

/* get the CPlayer, vec3, and euler classes */
#include "acStructs.hpp"

/* memory manager */
#include "../../pyMemory/pyMemory.hpp"

int main()
{
	/* create a manager for assaultCube. You can create multiple managers for multiple programs */
	while (!mem->attach(L"ac_client.exe"))
	{
		std::cout << "Assault Cube is not open" << std::endl;
		std::this_thread::sleep_for(std::chrono::seconds(1));
	}
	std::cout << "Attached to Assault Cube" << std::endl;
	auto attachTime = std::chrono::high_resolution_clock::now();

	/* Get the base address for assaultcube's main module. (this is also called ac_client.exe) */
	uint64_t ac_client = (uint64_t)mem->getModule(L"ac_client.exe");

	/* Main loop */
	DWORD lPlayerBase = mem->read<DWORD>(ac_client + 0x10f4f4);
	CPlayer lPlayer;
	euler currentLookAngles;
	int currentHealth;
	euler angles{0,0,0};
	uint64_t iterations = 0;
	double lastPrintTime = 0;

	/* IF YOU SEE THESE NEXT 4 LINES OF CODE, THEN I COMMITTED ON ACCIDENT, THIS IS NOT READY YET */
	//uintptr_t hpAddress = lPlayerBase + 0xf8;
	//int hpValue = mem->read<int>(hpAddress);
	//std::cout << "HP: " << hpValue << "stored at 0x" << std::hex << hpAddress << std::endl;
	//mem->scan<int>(hpValue);

	while (mem->processRunning()) /* while assaultcube is open */
	{
		auto now = std::chrono::high_resolution_clock::now();
		double tDelta = (std::chrono::duration_cast<std::chrono::microseconds>(now - attachTime).count())/((double)1000000);

		/* get the address of where localPlayer struct is stored. In assaultcube this is stored offset from the main module by 0x10f4f4 bytes */
		lPlayerBase = mem->read<DWORD>(ac_client + 0x10f4f4);

		/* read localplayer struct from memory (whose base was just gotten) */
		lPlayer = mem->read<CPlayer>(lPlayerBase);
		currentLookAngles = lPlayer.lookAngles;
		currentHealth = lPlayer.health;

		/* roll the screen left and right */
		float roll = sin(tDelta * 5) * 90;

		/* write the rolling angle to memory */
		mem->write<float>(lPlayerBase + offset::roll, roll);

		/* write 69420 to our health, because thats funny */
		mem->write<int>(lPlayerBase + offset::health, 69420);

		/* print the average (across the whole program time) iterations per second, every second */
		iterations++;
		if ((tDelta - lastPrintTime) > 1)
		{
			std::printf("Iterations per second: %f\t\t\r", iterations / tDelta);
			lastPrintTime = tDelta;
		}
	};

    return 0;
}
