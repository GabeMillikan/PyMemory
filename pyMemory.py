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

# Functions
kernel32.OpenProcess.argtypes = [wt.DWORD, wt.BOOL, wt.DWORD]
kernel32.OpenProcess.restype = wt.HANDLE

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

# Structures
class MODULEENTRY32(ct.Structure):
    _fields_ = [
        ( 'dwSize' , wt.DWORD ) , 
        ( 'th32ModuleID' , wt.DWORD ),
        ( 'th32ProcessID' , wt.DWORD ),
        ( 'GlblcntUsage' , wt.DWORD ),
        ( 'ProccntUsage' , wt.DWORD ) ,
        ( 'modBaseAddr' , ct.POINTER(wt.BYTE) ) ,
        ( 'modBaseSize' , wt.DWORD ) , 
        ( 'hModule' , wt.HMODULE ) ,
        ( 'szModule' , ct.c_char * 256 ),
        ( 'szExePath' , ct.c_char * 260 )
    ]

class MODULEINFO(ct.Structure):
    _fields_ = [
        ("lpBaseOfDll", wt.LPVOID),
        ("SizeOfImage", wt.DWORD),
        ("EntryPoint", wt.LPVOID)
    ]

class MEMORY_BASIC_INFORMATION(ct.Structure):
    _fields_ = [
        ('BaseAddress', wt.LPVOID),
        ('AllocationBase', wt.LPVOID),
        ('AllocationProtect', wt.DWORD),
        ('RegionSize', ct.c_size_t),
        ('State', wt.DWORD),
        ('Protect', wt.DWORD),
        ('Type', wt.DWORD),
    ]


'''
    Main Class
'''
class memory:
    def __init__(self, printErrors = False):
        self.printErrors = printErrors
        self.processName = 'unknown'
        self.processId = 0
        self.hProcess = 0
    
    # Opens the process with access rights and returns success status
    def attach(self, processName = None, processId = None):
        assert not (processName is None and processId is None), "To attach, must provide a processName or a processId"
        
        if processId is None:
            # we need a processId, so get it
            
            pid = None
            try:
                out = subprocess.check_output('tasklist /FI "imagename eq %s"' % (processName)).decode()
                
                # make sure the process is running
                assert not ("INFO: No tasks are running which match the specified criteria." in out), "process is not running"
                assert processName in out, "processName was not in the output"
                
                # Get the ID, which will be the first number listed after the processName
                after = out[out.index(processName) + len(processName):]
                match = re.search(r"\d+", after)
                
                assert not (match is None), "there was no processId listed after processName"
                
                pid = int(after[match.start():match.end()])
            except BaseException as e:
                if printErrors:
                    print("Encountered an error while trying to get processId from processName:")
                    print(">",str(e))
            
            if pid is None:
                if printErrors:
                    print("Failed to get processId from processName")
                return False # the user can error handle this
            
            processId = pid
        
        self.processId = processId
        self.processName = str(processName or "unknown")
        
        handle = None
        try:
            handle = kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, self.processId)
        except BaseException as e:
            if printErrors:
                print("Encountered an error while trying to OpenProcess with ALL_ACCESS:")
                print(">",str(e))
        
        if (handle == 0) or (handle is None):
            if printErrors:
                print("OpenProcess returned invalid handle, last error:", ct.get_last_error())
            return False
        
        self.hProcess = handle
        # this is the handle to the process that python now has read and write access for
        return True
    
    def getModuleNames(self):
        assert self.processId != 0, "Invalid process"
        
        names = []
        
        module = kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPMODULE | TH32CS_SNAPMODULE32, self.processId)
        moduleEntry = MODULEENTRY32()
        moduleEntry.dwSize = ct.sizeof(moduleEntry)
        
        while kernel32.Module32Next(module, ct.pointer(moduleEntry)):
            # add this one to the list
            names.append(moduleEntry.szModule.decode())
        
        return names