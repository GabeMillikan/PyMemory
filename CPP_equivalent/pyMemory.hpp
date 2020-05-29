#pragma once

#include <iostream>
#include <Windows.h>
#include <tlhelp32.h>


class memory
{
private:
	
public:
	HANDLE hProcess;
	DWORD processId;
	wchar_t* processName;

	memory();
	bool attach(wchar_t name[]);
	void listModules();
	uint64_t getModuleBase(wchar_t name[]);
	template <class T> T read(uint64_t address);
	template <class T> bool write(uint64_t address, T object);
	bool processRunning();
};

/* In python, pass the template class as an argument */
template<class T>
T memory::read(uint64_t address)
{
	T buffer;
	ReadProcessMemory(hProcess, (LPVOID)address, &buffer, sizeof(T), 0);
	return buffer;
}

template<class T>
bool memory::write(uint64_t address, T object)
{
	return WriteProcessMemory(hProcess, (LPVOID)address, &object, sizeof(T), 0);
}

static memory* mem = new memory();
