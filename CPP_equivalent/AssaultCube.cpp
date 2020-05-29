/*

This is an example usage of pyMemory by reading and writing AssaultCube's memory.
AssaultCube is a free (open source) first person shooter, avaliable at https://assault.cubers.net/

Except this is written in c++

*/

#include <iostream>
#include <chrono>
#include <thread>

/* get the CPlayer, vec3, and euler classes */
#include "pyMemory.hpp"

/* memory manager */
#include "acStructs.hpp"

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
	uint64_t ac_client = mem->getModuleBase(L"ac_client.exe");

	/* Main loop */
	DWORD lPlayerBase;
	CPlayer lPlayer;
	euler angles{0,0,0};
	uint64_t iterations = 0;
	double lastPrintTime = 0;

	while (mem->processRunning()) /* while assaultcube is open */
	{
		auto now = std::chrono::high_resolution_clock::now();
		double tDelta = (std::chrono::duration_cast<std::chrono::microseconds>(now - attachTime).count())/((double)1000000);

		/* get the address of where localPlayer struct is stored. In assaultcube this is stored offset from the main module by 0x10f4f4 bytes */
		lPlayerBase = mem->read<DWORD>(ac_client + 0x10f4f4);

		/* read localplayer struct from memory (whose base was just gotten) */
		lPlayer = mem->read<CPlayer>(lPlayerBase);
		angles = lPlayer.lookAngles;

		/* roll the screen left and right */
		angles.roll = float(sin(tDelta * 5) * 90);

		/* write the rolling angles to memory, which are stored 0x40 above localplayer */
		mem->write<euler>(lPlayerBase + 0x40, angles);

		/* write 69420 to our health, which are stored 0xf8 above localplayer, because thats funny */
		mem->write<int>(lPlayerBase + 0xf8, 69420);

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
