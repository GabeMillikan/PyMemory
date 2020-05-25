#include <iostream>
#include "pyMemory.hpp"

int main()
{
	memory* mem = new memory();
	bool success = mem->attach(L"ac_client.exe");

	DWORD ac_client = mem->getModuleBase(L"ac_client.exe");
	
	std::cout << "0x" << std::hex << ac_client << std::endl;

	while(1);
    return 0;
}

