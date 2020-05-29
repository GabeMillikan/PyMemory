import sys
c = sys.modules[__name__] # this library, ctype_helper
import ctypes as ct
from ctypes import wintypes as wt

# check if i can remove the "" prefixes without causing overlapping variable names
# As of 5/28/2020, there is no overlap. I doubt that this library will change much at all in the future,
# but i'll leave this check in because it only runs once on init, and doesn't take more than 10 ms
for ogName in dir(ct):
    typeValue = getattr(ct, ogName)
    # only allow actual types
    if "_type_" in dir(typeValue):
        if ogName.startswith("c_"):
            if (ogName[2:] in dir(ct)):
                quit("By changing variable '%s' to '%s', overlap is caused in ctypes" % (ogName, ogName[2:]))
            if (ogName[2:] in dir(wt)):
                quit("By changing variable '%s' to '%s', overlap is caused in ctypes.wintypes" % (ogName, ogName[2:]))

# allTypes all ctype types to a dict, without the  prefix
allTypes = {}
for ogName in dir(ct):
    typeValue = getattr(ct, ogName)
    # only allow actual types
    if "_type_" in dir(typeValue):
        name = ogName[2:] if ogName.startswith("c_") else ogName
        allTypes[name] = typeValue

# Add all wintype types to the dict, they have no prefix, but are all caps... add lowercase equivalents
for name in dir(wt):
    typeValue = getattr(wt, name)
    # only allow actual types
    if "_type_" in dir(typeValue):
        allTypes[name] = typeValue
        allTypes[name.lower()] = typeValue

# create pointers for each type, append "_p" to the name
pointerTypes = {}
for typeName in allTypes:
    typeValue = allTypes[typeName]
    ptrName = typeName + "_p"
    ptrType = ct.POINTER(typeValue)
    pointerTypes[ptrName] = ptrType
    
# add pointers to allTypes
allTypes.update(pointerTypes)

# unpack all values in the allTypes dict to this module
for typeName in allTypes:
    typeValue = allTypes[typeName]
    setattr(c, typeName, typeValue)

# now unpack the rest of the ctypes, that are NOT listed in allTypes (like buffer, which was omitted above)
# do not incldue dunder methods
for thingName in dir(ct):
    typeValue = getattr(ct, thingName)
    name = thingName[2:] if (thingName.startswith("c_") and isinstance(typeValue, type)) else thingName
    if (name.startswith("__")) or (name in allTypes):
        continue
    setattr(c, name, typeValue)

# same as above but for wintypes
for thingName in dir(wt):
    typeValue = getattr(wt, thingName)
    name = thingName[2:] if (thingName.startswith("") and isinstance(typeValue, type)) else thingName
    if (name.startswith("__")) or (name in allTypes):
        continue
    setattr(c, name, typeValue)
    

# at this point, we can access ctypes or wintypes by just putting `char` or `dword_p` instead of `ct.char` or `ct.POINTER(wt.DWORD)`
# also, we can use functions like `byref` instead of `ct.byref`
# print(byref(dword_p(dword(20)))) => print( &&(DWORD)20 )

# open DLLs
kernel32 = WinDLL('kernel32', use_last_error = True)

# Windows Structures
def createStruct(*args):
    global _custom_class_count
    
    f = []
    for i in range(0, len(args), 2):
        type, name = args[i], args[i+1]
        f.append((name, type))
    
    class CC(Structure):
        _fields_ = f
    
    return CC

MODULEENTRY32 = createStruct(
    DWORD,      'dwSize',
    DWORD,      'th32ModuleID',
    DWORD,      'th32ProcessID',
    DWORD,      'GlblcntUsage',
    DWORD,      'ProccntUsage',
    BYTE_p,     'modBaseAddr',
    DWORD,      'modBaseSize',
    HMODULE,    'hModule',
    char * 256, 'szModule',
    char * 260, 'szExePath',
)

MODULEINFO = createStruct(
    LPVOID, 'lpBaseOfDll',
    DWORD,  'SizeOfImage',
    LPVOID, 'EntryPoint',
)

MEMORY_BASIINFORMATION = createStruct(
    LPVOID, 'BaseAddress',
    LPVOID, 'AllocationBase',
    DWORD,  'AllocationProtect',
    size_t, 'RegionSize',
    DWORD,  'State',
    DWORD,  'Protect',
    DWORD,  'Type',
)

PROCESSENTRY32 = createStruct(
    DWORD,    'dwSize',
    DWORD,    'cntUsage',
    DWORD,    'th32ProcessID',
    ulong_p,  'th32DefaultHeapID',
    DWORD,    'th32ModuleID',
    DWORD,    'cntThreads',
    DWORD,    'th32ParentProcessID',
    long,     'pcPriClassBase',
    DWORD,    'dwFlags',
    char*260, 'szExeFile',
)

# Functions
kernel32.OpenProcess.argtypes = [DWORD, BOOL, DWORD]
kernel32.OpenProcess.restype = HANDLE

kernel32.CloseHandle.argtypes = [HANDLE]
kernel32.CloseHandle.restype = BOOL

kernel32.Process32First.argtypes = [HANDLE, POINTER(PROCESSENTRY32)]
kernel32.Process32First.restype = BOOL

kernel32.Process32Next.argtypes = [HANDLE, POINTER(PROCESSENTRY32)]
kernel32.Process32Next.restype = BOOL

kernel32.Module32Next.argtypes = [HANDLE, POINTER(MODULEENTRY32)]
kernel32.Module32Next.restype = BOOL

kernel32.GetExitCodeProcess.argtypes = [HANDLE, DWORD_p]
kernel32.GetExitCodeProcess.restype = BOOL

kernel32.ReadProcessMemory.argtypes = [HANDLE, LPVOID, LPVOID, size_t, size_t_p]
kernel32.ReadProcessMemory.restype = BOOL

kernel32.WriteProcessMemory.argtypes = [HANDLE, LPVOID, LPVOID, size_t, size_t_p]
kernel32.WriteProcessMemory.restype = BOOL

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

STILL_ACTIVE = 0x00000103