import ctypes
from ctypes import wintypes
import struct
import win32com.client

C_PROCESS_ALL_ACCESS  = 0x1F0FFF
C_TH32CS_SNAPHEAPLIST = 0x00000001
C_TH32CS_SNAPPROCESS  = 0x00000002
C_TH32CS_SNAPTHREAD   = 0x00000004
C_TH32CS_SNAPMODULE   = 0x00000008
C_TH32CS_SNAPMODULE32 = 0x00000010
C_TH32CS_SNAPALL      = (C_TH32CS_SNAPHEAPLIST | C_TH32CS_SNAPPROCESS | C_TH32CS_SNAPTHREAD | C_TH32CS_SNAPMODULE)
C_TH32CS_INHERIT      = 0x80000000

def get_process_id(process_name):
    wmi = win32com.client.GetObject('winmgmts:')
    for p in wmi.InstancesOf('win32_process'):
        if p.Name == process_name:
            try:
                return int(p.Properties_('ProcessId'))
            except Exception as e:
                pass
    return 0
    
    
class _MODULEENTRY32(ctypes.Structure):
    _fields_ = [( 'dwSize' , wintypes.DWORD ) , 
                ( 'th32ModuleID' , wintypes.DWORD ),
                ( 'th32ProcessID' , wintypes.DWORD ),
                ( 'GlblcntUsage' , wintypes.DWORD ),
                ( 'ProccntUsage' , wintypes.DWORD ) ,
                ( 'modBaseAddr' , ctypes.POINTER(wintypes.BYTE) ) ,
                ( 'modBaseSize' , wintypes.DWORD ) , 
                ( 'hModule' , wintypes.HMODULE ) ,
                ( 'szModule' , ctypes.c_char * 256 ),
                ( 'szExePath' , ctypes.c_char * 260 ) ]

_size_by_structrep = {
    "c" : 1,
    "b" : 1,
    "B" : 1,
    "?" : 1,
    
    "h" : 2,
    "H" : 2,
    
    "i" : 4,
    "I" : 4,
    "l" : 4,
    "L" : 4,
    "f" : 4,
    
    "q" : 8,
    "Q" : 8,
    "d" : 8,
}

class vartype:
    _int = int
    _float = float
    class char:
        structrep = "c"
        size = _size_by_structrep['c']
        default = b' '
    class signed_char:
        structrep = "b"
        size = _size_by_structrep['b']
        default = b' '
    class unsigned_char:
        structrep = "B"
        size = _size_by_structrep['B']
        default = b' '
    class bool:
        structrep = "?"
        size = _size_by_structrep['?']
        default = False
    class short:
        structrep = "h"
        size = _size_by_structrep['h']
        default = int(0)
    class unsigned_short:
        structrep = "H"
        size = _size_by_structrep['H']
        default = int(0)
    class int:
        structrep = "i"
        size = _size_by_structrep['i']
        default = int(0)
    class unsigned_int:
        structrep = "I"
        size = _size_by_structrep['I']
        default = int(0)
    class long:
        structrep = "l"
        size = _size_by_structrep['l']
        default = int(0)
    class unsigned_long:
        structrep = "L"
        size = _size_by_structrep['L']
        default = int(0)
    class long_long:
        structrep = "q"
        size = _size_by_structrep['q']
        default = int(0)
    class unsigned_long_long:
        structrep = "Q"
        size = _size_by_structrep['Q']
        default = int(0)
    class float:
        structrep = "f"
        size = _size_by_structrep['f']
        default = float(0)
    class double:
        structrep = "d"
        size = _size_by_structrep['d']
        default = float(0)
    class char_array:
        def __init__(self, length):
            self.__len__ = lambda *args: length
            self.default = b' '
            self.size = length
            self.structrep = 'c'*length  

class memory_struct:
    def __init__(self):
        self._offsets = {}
        self._values  = {}
        self._struct  = []
        self.size = 0x0
        self.base = 0x0
    
    def set_base(self, addr):
        self.base = addr
    
    def add_offset(self, offset, name, type):
        assert isinstance(name, str), "Name must be a string object"
        self._offsets[name] = offset
        self._values[name] = type.default
        self._struct.append([name, type])
        self._struct = sorted(self._struct, key = lambda v: self._offsets[v[0]])
        
        if (offset + type.size) > self.size:
            self.size = offset + type.size
        
    def get_decode_str(self):
        s = ''
        
        last_addr = 0x0
        for [name, type] in self._struct:
            cur_addr = self._offsets[name]
            addr_dst = cur_addr - last_addr
            
            for i in range(addr_dst):
                s += vartype.char.structrep
                
            s += type.structrep
            
            last_addr = cur_addr + type.size
            
        return s
        
    def __getitem__(self, key):
        return self._values[key]
        
    def __setitem__(self, key, value):
        self._values[key] = value
        
    def get_buffer(self):  
        args    = []
        codestr = ''
        
        last_addr = 0x0
        for [name, type] in self._struct:
            cur_addr = self._offsets[name]
            addr_dst = cur_addr - last_addr
            
            for i in range(addr_dst):
                args.append(vartype.char.default)
                codestr += vartype.char.structrep
                
            if isinstance(type, vartype.char_array):
                for i in range(type.__len__()):
                    args.append(self[name].encode('utf-8'))
                codestr += type.structrep
            else:
                if type is vartype.char:
                    args.append(self[name].encode('utf-8'))
                else:
                    args.append(self[name])
                codestr += type.structrep
            
            last_addr = cur_addr + type.size
        return struct.pack(codestr, *args)
        
    def __str__(self):
        s = ''
        for [name, type] in self._struct:
            s += name + " : " + str(self[name]) + "\n"
        return s

class memory:
    def __init__(self):
        pass
        
    def attach_by_process_name(self, process_name):
        self.processid = get_process_id(process_name)
        if not self.processid:
            return False
        return self.attach_by_processid(self.processid)
        
    def attach_by_processid(self, processid):
        if not processid:
            return False
        self.processid = processid
        
        try:
            self.kernel32 = ctypes.windll.kernel32
            
            self.open_process = self.kernel32.OpenProcess
            self.open_process.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
            self.open_process.restype = wintypes.HANDLE
            
            self.__c_read_proccess_memory__ = self.kernel32.ReadProcessMemory
            self.__c_read_proccess_memory__.argtypes = [wintypes.HANDLE, wintypes.LPCVOID, wintypes.LPVOID, ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t)]
            self.__c_read_proccess_memory__.restype = wintypes.BOOL
            
            self.__c_write_proccess_memory__ = self.kernel32.WriteProcessMemory
            self.__c_write_proccess_memory__.argtypes = [wintypes.HANDLE, wintypes.LPCVOID, wintypes.LPVOID, ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t)]
            self.__c_write_proccess_memory__.restype = wintypes.BOOL
            
            self.hProcess = self.open_process(C_PROCESS_ALL_ACCESS, False, int(self.processid))
            return True, 0
        except Exception as e:
            return False, e
        return False, "Try/Except returned nothing somehow..."
    
    def get_module(self, moduleName):
        module = self.kernel32.CreateToolhelp32Snapshot(C_TH32CS_SNAPMODULE | C_TH32CS_SNAPMODULE32, self.processid)
        moduleEntry = _MODULEENTRY32()
        moduleEntry.dwSize = ctypes.sizeof(moduleEntry)

        while self.kernel32.Module32Next(module, ctypes.pointer(moduleEntry)):
            if (moduleEntry.szModule.decode() == moduleName):
                self.kernel32.CloseHandle(module)
                return struct.unpack("I", moduleEntry.modBaseAddr)[0]
                
        self.kernel32.CloseHandle(module)
        return 0
    
    def read(self, address, var_type):
        buffer = ctypes.create_string_buffer(var_type.size)
        success = self.__c_read_proccess_memory__(
                          # hProcess
                          self.hProcess,
                          # (LPVOID)address
                          ctypes.c_void_p(address),
                          # &buffer
                          buffer,
                          # sizeof(buffer) -> should equal var_type.size
                          ctypes.sizeof(buffer),
                          # nullptr
                          ctypes.POINTER(wintypes.DWORD)(wintypes.DWORD(0))
                          )
        u = struct.unpack(var_type.structrep, buffer)
        if isinstance(var_type, vartype.char_array):
            # concatenate then decode and return char array
            try:
                v = ''
                for b in u:
                    try:
                        v += b.decode()
                    except Exception as e:
                        v += " "
                return v
            except Exception as e:
                pass
            return var_type.default
        elif var_type is vartype.char:
            # decode and return char
            try:
                return u[0].decode()
            except Exception as e:
                pass
            return var_type.default
        # return numeric types
        return u[0]
        
    def write(self, address, var_type, value):
        buffer = 0
        bytesize = 0
        if isinstance(var_type, vartype.char_array):
            buffer = struct.pack(var_type.structrep, *[c for c in value])
            bytesize = len(value)
        else:
            buffer = struct.pack(var_type.structrep, value)
            bytesize = var_type.size
        return self.__c_write_proccess_memory__(
                          # hProcess
                          self.hProcess,
                          # (LPVOID)address
                          ctypes.c_void_p(address),
                          # &buffer
                          buffer,
                          # sizeof(buffer)
                          bytesize,
                          # nullptr
                          ctypes.POINTER(wintypes.DWORD)(wintypes.DWORD(0))
                          )
                          
    def readto(self, memstruct):
        buffer = ctypes.create_string_buffer(memstruct.size)
        success = self.__c_read_proccess_memory__(
                          # hProcess
                          self.hProcess,
                          # (LPVOID)address
                          ctypes.c_void_p(memstruct.base),
                          # &buffer
                          buffer,
                          # sizeof(buffer) -> should equal var_type.size
                          ctypes.sizeof(buffer),
                          # nullptr
                          ctypes.POINTER(wintypes.DWORD)(wintypes.DWORD(0))
                          )
        codestr = memstruct.get_decode_str()
        mem = struct.unpack(codestr, buffer)
        
        items_before_current = 0
        last_addr = 0x0
        for [name, type] in memstruct._struct:
            cur_addr = memstruct._offsets[name]
            addr_dst = cur_addr - last_addr
            items_before_current += addr_dst
            
            if isinstance(type, vartype.char_array):
                s = ''
                for i in range(type.__len__()):
                    try:
                        s += mem[items_before_current].decode()
                    except Exception as e:
                        s += vartype.char.default.decode()
                    items_before_current += 1
                memstruct[name] = s
            else:
                memstruct[name] = mem[items_before_current]
                items_before_current += 1
            last_addr = cur_addr + type.size
        
        return True

    def writefrom(self, memstruct):
        buffer = memstruct.get_buffer()
        return self.__c_write_proccess_memory__(
                          # hProcess
                          self.hProcess,
                          # (LPVOID)address
                          ctypes.c_void_p(memstruct.base),
                          # &buffer
                          buffer,
                          # sizeof(buffer)
                          memstruct.size,
                          # nullptr
                          ctypes.POINTER(wintypes.DWORD)(wintypes.DWORD(0))
                          )
        
        
        
