import ctype_helper as c
import subprocess
import re

'''
    Main Class for attaching, reading, and writing to memory
'''
class memory:
    def __init__(self, printErrors = False):
        self.processName = 'unknown'
        self.processId = 0
        self.hProcess = 0
    
    # Opens the process with access rights and returns success status
    def attach(self, processName):
        '''
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
        '''
        entry = c.PROCESSENTRY32()
        entry.dwSize = c.sizeof(c.PROCESSENTRY32)
        snapshot = c.kernel32.CreateToolhelp32Snapshot(c.TH32CS_SNAPPROCESS, 0)
        
        success = False;
        if (c.kernel32.Process32First(snapshot, c.byref(entry))):
            while (c.kernel32.Process32Next(snapshot, c.byref(entry))):
                if (entry.szExeFile.decode('utf-8') == processName):
                    self.hProcess = c.kernel32.OpenProcess(c.PROCESS_ALL_ACCESS, False, entry.th32ProcessID)
                    self.processId = entry.th32ProcessID
                    self.processName = processName
                    success = True
                    break
        
        c.kernel32.CloseHandle(snapshot)
        return success
        
    def getModuleNames(self):
        '''
        /* I don't feel like dealing with c++ arrays, so im just gonna print them out */
        /* in python, make a a list of names and return it */
        
        HANDLE snapshot = CreateToolhelp32Snapshot(TH32CS_SNAPMODULE | TH32CS_SNAPMODULE32, this->processId);
        MODULEENTRY32 moduleEntry = MODULEENTRY32();
        moduleEntry.dwSize = sizeof(moduleEntry);

        while (Module32Next(snapshot, &moduleEntry))
            std::wcout << moduleEntry.szModule << std::endl;

        CloseHandle(snapshot);
        '''
        names = []
        
        snapshot = c.kernel32.CreateToolhelp32Snapshot(c.TH32CS_SNAPMODULE | c.TH32CS_SNAPMODULE32, self.processId)
        moduleEntry = c.MODULEENTRY32()
        moduleEntry.dwSize = c.sizeof(moduleEntry)
        
        while (kernel32.Module32Next(snapshot, c.byref(moduleEntry))):
            names.append(moduleEntry.szModule.decode('utf-8'))
        
        c.kernel32.CloseHandle(snapshot)
        return names
    
    def getModuleBase(self, name):
        '''
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
        '''
        snapshot = c.kernel32.CreateToolhelp32Snapshot(c.TH32CS_SNAPMODULE | c.TH32CS_SNAPMODULE32, self.processId)
        moduleEntry = c.MODULEENTRY32()
        moduleEntry.dwSize = c.sizeof(moduleEntry)
        
        while (c.kernel32.Module32Next(snapshot, c.byref(moduleEntry))):
            if (moduleEntry.szModule.decode('utf-8') == name):
                return moduleEntry.hModule # python `int` instance
        
        c.kernel32.CloseHandle(snapshot)
        return 0
    
    def read(self, address, type = c.int):
        '''
        /* In python, pass the template class as an argument */
        template<class T>
        T memory::read(uint64_t address)
        {
            T buffer;
            ReadProcessMemory(hProcess, (LPVOID)address, &buffer, sizeof(T), 0);
            return buffer;
        }
        '''
        buffer = type()
        c.kernel32.ReadProcessMemory(self.hProcess, c.LPVOID(address), c.byref(buffer), c.sizeof(type), c.byref(c.ulong(0)))
        return buffer # note that this will still have the ctype type, so you'll need to do "memory.read(0x69, type = c.DWORD).value"
    
    def write(self, address, object):
        '''
        template<class T>
        bool memory::write(uint64_t address, T object)
        {
            return WriteProcessMemory(hProcess, (LPVOID)address, &object, sizeof(T), 0);
        }
        '''
        return c.kernel32.WriteProcessMemory(self.hProcess, c.LPVOID(address), c.byref(object), c.sizeof(object), c.byref(c.ulong(0)))
        
    def processRunning(self):
        '''
        DWORD code;
        return GetExitCodeProcess(this->hProcess, &code) && (code == STILL_ACTIVE);
        '''
        code = c.DWORD()
        return c.kernel32.GetExitCodeProcess(self.hProcess, c.byref(code)) and (code.value == c.STILL_ACTIVE)
        
