import ctypes as ct
from ctypes import wintypes as wt
import subprocess
import re

'''
    Setup ctypes
'''
kernel32 = ct.WinDLL('kernel32', use_last_error = True)

# types
ct.c_size_t_p = ct.POINTER(ct.c_size_t)
ct.c_ulong_p = ct.POINTER(ct.c_ulong)

class MODULEENTRY32(ct.Structure):
    _fields_ = [
        ( 'dwSize'        , wt.DWORD            ), 
        ( 'th32ModuleID'  , wt.DWORD            ),
        ( 'th32ProcessID' , wt.DWORD            ),
        ( 'GlblcntUsage'  , wt.DWORD            ),
        ( 'ProccntUsage'  , wt.DWORD            ),
        ( 'modBaseAddr'   , ct.POINTER(wt.BYTE) ),
        ( 'modBaseSize'   , wt.DWORD            ), 
        ( 'hModule'       , wt.HMODULE          ),
        ( 'szModule'      , ct.c_char * 256     ),
        ( 'szExePath'     , ct.c_char * 260     ),
    ]


class PROCESSENTRY32(ct.Structure):
    _fields_ = [
        ( 'dwSize'              , wt.DWORD        ),
        ( 'cntUsage'            , wt.DWORD        ),
        ( 'th32ProcessID'       , wt.DWORD        ),
        ( 'th32DefaultHeapID'   , ct.c_ulong_p    ),
        ( 'th32ModuleID'        , wt.DWORD        ),
        ( 'cntThreads'          , wt.DWORD        ),
        ( 'th32ParentProcessID' , wt.DWORD        ),
        ( 'pcPriClassBase'      , ct.c_long       ),
        ( 'dwFlags'             , wt.DWORD        ),
        ( 'szExeFile'           , ct.c_char * 260 ), # actually wchar, but i think ctypes automatically converts?
    ]


class MODULEINFO(ct.Structure):
    _fields_ = [
        ( 'lpBaseOfDll' , wt.LPVOID ),
        ( 'SizeOfImage' , wt.DWORD  ),
        ( 'EntryPoint'  , wt.LPVOID ),
    ]

class MEMORY_BASIC_INFORMATION(ct.Structure):
    _fields_ = [
        ( 'BaseAddress'       , wt.LPVOID   ),
        ( 'AllocationBase'    , wt.LPVOID   ),
        ( 'AllocationProtect' , wt.DWORD    ),
        ( 'RegionSize'        , ct.c_size_t ),
        ( 'State'             , wt.DWORD    ),
        ( 'Protect'           , wt.DWORD    ),
        ( 'Type'              , wt.DWORD    ),
    ]

# Functions
kernel32.OpenProcess.argtypes = [wt.DWORD, wt.BOOL, wt.DWORD]
kernel32.OpenProcess.restype = wt.HANDLE

kernel32.CloseHandle.argtypes = [wt.HANDLE, ]
kernel32.CloseHandle.restype = wt.BOOL

kernel32.Process32First.argtypes = [wt.HANDLE, ct.POINTER(PROCESSENTRY32)]
kernel32.Process32First.restype = wt.BOOL

kernel32.Process32Next.argtypes = [wt.HANDLE, ct.POINTER(PROCESSENTRY32)]
kernel32.Process32Next.restype = wt.BOOL

kernel32.Module32Next.argtypes = [wt.HANDLE, ct.POINTER(MODULEENTRY32)]
kernel32.Module32Next.restype = wt.BOOL

kernel32.ReadProcessMemory.argtypes = [wt.HANDLE, wt.LPVOID, wt.LPVOID, ct.c_size_t, ct.c_size_t_p]
kernel32.ReadProcessMemory.restype = wt.BOOL

# Constants
PROCESS_TERMINATE                  = 0x0001
PROCESS_CREATE_THREAD              = 0x0002
PROCESS_SET_SESSIONID              = 0x0004
PROCESS_VM_OPERATION               = 0x0008
PROCESS_VM_READ                    = 0x0010
PROCESS_VM_WRITE                   = 0x0020
PROCESS_DUP_HANDLE                 = 0x0040
PROCESS_CREATE_PROCESS             = 0x0080
PROCESS_SET_QUOTA                  = 0x0100
PROCESS_SET_INFORMATION            = 0x0200
PROCESS_QUERY_INFORMATION          = 0x0400
PROCESS_SUSPEND_RESUME             = 0x0800
PROCESS_QUERY_LIMITED_INFORMATION  = 0x1000
PROCESS_SET_LIMITED_INFORMATION    = 0x2000
SYNCHRONIZE                        = 0x00100000
STANDARD_RIGHTS_REQUIRED           = 0x000F0000
PROCESS_ALL_ACCESS                 = (STANDARD_RIGHTS_REQUIRED | SYNCHRONIZE | 0xFFFF)

PAGE_NOACCESS          = 0x01
PAGE_READONLY          = 0x02
PAGE_READWRITE         = 0x04
PAGE_WRITECOPY         = 0x08
PAGE_EXECUTE           = 0x10
PAGE_EXECUTE_READ      = 0x20
PAGE_EXECUTE_READWRITE = 0x40
PAGE_EXECUTE_WRITECOPY = 0x80
PAGE_GUARD             = 0x100
PAGE_NOCACHE           = 0x200

MEM_COMMIT             = 0x1000
MEM_RESERVE            = 0x2000
MEM_FREE               = 0x10000
MEM_PRIVATE            = 0x20000
MEM_MAPPED             = 0x40000
MEM_IMAGE              = 0x1000000

TH32CS_SNAPHEAPLIST = 0x00000001
TH32CS_SNAPPROCESS  = 0x00000002
TH32CS_SNAPTHREAD   = 0x00000004
TH32CS_SNAPMODULE   = 0x00000008
TH32CS_SNAPMODULE32 = 0x00000010
TH32CS_SNAPALL      = (TH32CS_SNAPHEAPLIST | TH32CS_SNAPPROCESS | TH32CS_SNAPTHREAD | TH32CS_SNAPMODULE)
TH32CS_INHERIT      = 0x80000000


'''
    Main Class
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
        entry = PROCESSENTRY32()
        entry.dwSize = ct.sizeof(PROCESSENTRY32)
        snapshot = kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
        
        success = False;
        if (kernel32.Process32First(snapshot, ct.byref(entry))):
            while (kernel32.Process32Next(snapshot, ct.byref(entry))):
                if (entry.szExeFile.decode('utf-8') == processName):
                    self.hProcess = kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, entry.th32ProcessID)
                    self.processId = entry.th32ProcessID
                    self.processName = processName
                    success = True
                    break
        
        kernel32.CloseHandle(snapshot)
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
        
        snapshot = kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPMODULE | TH32CS_SNAPMODULE32, self.processId)
        moduleEntry = MODULEENTRY32()
        moduleEntry.dwSize = ct.sizeof(moduleEntry)
        
        while (kernel32.Module32Next(snapshot, ct.byref(moduleEntry))):
            names.append(moduleEntry.szModule.decode('utf-8'))
        
        kernel32.CloseHandle(snapshot)
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
        snapshot = kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPMODULE | TH32CS_SNAPMODULE32, self.processId)
        moduleEntry = MODULEENTRY32()
        moduleEntry.dwSize = ct.sizeof(moduleEntry)
        
        while (kernel32.Module32Next(snapshot, ct.byref(moduleEntry))):
            if (moduleEntry.szModule.decode('utf-8') == name):
                return moduleEntry.hModule # python `int` instance
        
        kernel32.CloseHandle(snapshot)
        return 0
    
    def read(self, address, type = ct.c_int):
        '''
        /* In python, pass the template class as an argument */
        template<class T>
        T memory::read(uint32_t address)
        {
            T buffer;
            ReadProcessMemory(hProcess, (LPVOID)address, &buffer, sizeof(T), 0);
            return buffer;
        }
        '''
        buffer = type()
        kernel32.ReadProcessMemory(self.hProcess, wt.LPVOID(address), ct.byref(buffer), ct.sizeof(type), ct.byref(ct.c_ulong(0)))
        return buffer # note that this will still have the ctype type, so you'll need to do "memory.read(0x69, type = wt.DWORD).value"
    
    def write(self, address, object):
        '''
        template<class T>
        bool memory::write(uint32_t address, T object)
        {
            return WriteProcessMemory(hProcess, (LPVOID)address, &object, sizeof(T), 0);
        }
        '''
        return kernel32.WriteProcessMemory(self.hProcess, wt.LPVOID(address), ct.byref(object), ct.sizeof(object), ct.byref(ct.c_ulong(0)))
        
        
