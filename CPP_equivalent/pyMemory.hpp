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
	DWORD getModuleBase(wchar_t name[]);
};