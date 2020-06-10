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
	/* I don't feel like dealing with c++ arrays, so im just gonna print them out */
	/* in python, make a a list of names and return it */

	HANDLE snapshot = CreateToolhelp32Snapshot(TH32CS_SNAPMODULE | TH32CS_SNAPMODULE32, this->processId);
	MODULEENTRY32 moduleEntry = MODULEENTRY32();
	moduleEntry.dwSize = sizeof(moduleEntry);

	while (Module32Next(snapshot, &moduleEntry))
		std::wcout << moduleEntry.szModule << std::endl;

	CloseHandle(snapshot);
}

HMODULE memory::getModule(wchar_t name[])
{
	HANDLE snapshot = CreateToolhelp32Snapshot(TH32CS_SNAPMODULE | TH32CS_SNAPMODULE32, this->processId);
	MODULEENTRY32 moduleEntry = MODULEENTRY32();
	moduleEntry.dwSize = sizeof(moduleEntry);

	while (Module32Next(snapshot, &moduleEntry))
		if (int(wcscmp(moduleEntry.szModule, name)) == 0)
		{
			return moduleEntry.hModule; //DLL's base addr wrt the process
		}
	
	CloseHandle(snapshot);
	return 0;
}

bool memory::processRunning()
{
	DWORD code;
	return GetExitCodeProcess(this->hProcess, &code) && (code == STILL_ACTIVE);
}