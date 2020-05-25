#include "pyMemory.hpp"

memory::memory(){}

bool memory::attach(wchar_t name[])
{
	PROCESSENTRY32 entry;
	entry.dwSize = sizeof(PROCESSENTRY32);
	HANDLE snapshot = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, NULL);

	bool success = false;
	if (Process32First(snapshot, &entry))
	{
		while (Process32Next(snapshot, &entry))
		{
			if (int(wcscmp(entry.szExeFile, name)) == 0)
			{
				this->hProcess = OpenProcess(PROCESS_ALL_ACCESS, FALSE, entry.th32ProcessID);
				this->processId = entry.th32ProcessID;
				this->processName = entry.szExeFile;
				success = true;
				break;
			}
		}
	}

	CloseHandle(snapshot);
	return success;
}

void memory::listModules()
{
	HANDLE snapshot = CreateToolhelp32Snapshot(TH32CS_SNAPMODULE | TH32CS_SNAPMODULE32, this->processId);
	MODULEENTRY32 moduleEntry = MODULEENTRY32();
	moduleEntry.dwSize = sizeof(moduleEntry);

	while (Module32Next(snapshot, &moduleEntry))
		std::wcout << moduleEntry.szModule << std::endl;
}

DWORD memory::getModuleBase(wchar_t name[])
{
	HANDLE snapshot = CreateToolhelp32Snapshot(TH32CS_SNAPMODULE | TH32CS_SNAPMODULE32, this->processId);
	MODULEENTRY32 moduleEntry = MODULEENTRY32();
	moduleEntry.dwSize = sizeof(moduleEntry);

	while (Module32Next(snapshot, &moduleEntry))
		if (int(wcscmp(moduleEntry.szModule, name)) == 0)
		{
			return (DWORD)moduleEntry.hModule; //DLL's base addr wrt the process
		}
	
	CloseHandle(snapshot);
	return 0;
}