#include <iostream>
#include "pyMemory.hpp"
#include <chrono>
#include <thread>

int main()
{
	memory* mem = new memory();
	
	/* Attach to assault cube (OpenProcess) */
	while (!mem->attach(L"ac_client.exe"))
	{
		std::cout << "Assault Cube is not open" << std::endl;
		std::this_thread::sleep_for(std::chrono::seconds(1));
	}
	std::cout << "Attached to Assault Cube" << std::endl;

	/* Get modules */
	DWORD ac_client = mem->getModuleBase(L"ac_client.exe");
	std::cout << "ac_client.exe -> 0x" << std::hex << ac_client << std::endl;

	/* Get LocalPlayer address */
	std::cout << std::endl;
	DWORD localPlayerBase = mem->read<DWORD>(ac_client + 0x10f4f4);
	std::cout << "0x" << std::hex << localPlayerBase << std::dec << std::endl;

	/* Periodically print health */
	std::cout << std::endl;
	while (true)
	{
		int hp = mem->read<int>(localPlayerBase + 0xf8);
		std::cout << "Current Health: " << hp << "\t\r";
		std::this_thread::sleep_for(std::chrono::milliseconds(1));
	};

    return 0;
}
