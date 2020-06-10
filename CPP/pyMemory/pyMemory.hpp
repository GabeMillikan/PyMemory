#pragma once

#include <iostream>
#include <Windows.h>
#include <psapi.h>
#include <tlhelp32.h>

#define PAGE_READABLE (PAGE_READONLY | PAGE_READWRITE | PAGE_WRITECOPY | PAGE_EXECUTE | PAGE_EXECUTE_READ | PAGE_EXECUTE_READWRITE | PAGE_EXECUTE_WRITECOPY)

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
	HMODULE getModule(wchar_t name[]);
	template <class T> T read(uint64_t address);
	template <class T> bool write(uint64_t address, T object);
	bool processRunning();
	template<class T> void scanModule(HMODULE searchModule, T search);
	template<class T> void scan(T search);
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

/* please ignore the existance of this function for now, its not ready yet (i'm working on it) */
/* Unfortunately, if an object is stored across multiple pages, this scanner will not find it */
template<class T>
void memory::scanModule(HMODULE searchModule, T search)
{
	/* the bytes that we are looking for in memory, and how many*/
	char* searchBytes = (char*)(&search);
	size_t nSearchBytes = sizeof(T);

	/* get information about the module we are searching */
	MODULEINFO mInfo;
	GetModuleInformation(this->hProcess, searchModule, &mInfo, sizeof(mInfo));

	/* get address range that the module has in memory */
	char* addressLow = (char*)mInfo.lpBaseOfDll;
	char* addressHigh = addressLow + mInfo.SizeOfImage;

	/* allocate some space to copy pages into my own memory */
	char* pageBytes = (char*)malloc(1024);
	size_t nPageBytes = 1024;

	/* loop through pages of memory that are committed and readable */
	MEMORY_BASIC_INFORMATION page = {};
	char* address = addressLow;
	while (address < addressHigh)
	{
		// shouldnt ever fail, but you know, might as well check
		if (!VirtualQueryEx(this->hProcess, (LPCVOID)address, &page, sizeof(page)))
		{
			//std::cout << "VQE fail" << std::endl;
			address++;
			continue;
		}

		// only check pages that have been allocated
		if (!(page.State & MEM_COMMIT))
		{
			//std::cout << "not committed" << std::endl;
			address++;
			continue;
		}

		// gaurded pages are non-accessable
		if (page.Protect & PAGE_GUARD)
		{
			//std::cout << "gaurded" << std::endl;
			address++;
			continue;
		}

		// make sure it's readable
		if (!(page.Protect & PAGE_READABLE))
		{
			//std::cout << "non readable" << std::endl;
			address++;
			continue;
		}

		// if the page size is larger than the current space i allocated, then allocate new, larger space
		if (page.RegionSize > nPageBytes)
		{
			free(pageBytes);
			pageBytes = (char*)malloc(page.RegionSize);
			nPageBytes = page.RegionSize;
		}

		// read the page into my own memory
		if (!ReadProcessMemory(this->hProcess, page.BaseAddress, pageBytes, page.RegionSize, 0))
		{
			std::cout << "RPM fail" << std::endl;
			address++;
			continue;
		}

		// scan the read bytes for searchBytes
		for (size_t searchOffset = 0; searchOffset < page.RegionSize - nSearchBytes; ++searchOffset)
		{
			// check if the searchbytes are stored at page + offset
			bool found = true;
			for (size_t j = 0; j < nSearchBytes; j++)
			{
				if (searchBytes[j] != pageBytes[searchOffset + j])
				{
					found = false;
					break;
				}
			}

			if (found)
			{
				char* matchAt = address + searchOffset;
				std::cout << " 0x" << std::hex << uint64_t(matchAt) << std::endl;
			}
		}

		// increment address
		address += page.RegionSize;

		// reset the page info
		page = {};
	}
}

// call scanModule for every module in process
template<class T>
void memory::scan(T search)
{
	HANDLE snapshot = CreateToolhelp32Snapshot(TH32CS_SNAPMODULE | TH32CS_SNAPMODULE32, this->processId);
	MODULEENTRY32 moduleEntry = MODULEENTRY32();
	moduleEntry.dwSize = sizeof(moduleEntry);

	while (Module32Next(snapshot, &moduleEntry))
	{
		std::wcout << L"Scanning " << moduleEntry.szModule << std::endl;
		this->scanModule<T>(moduleEntry.hModule, search);
	}

	CloseHandle(snapshot);
}

static memory* mem = new memory();