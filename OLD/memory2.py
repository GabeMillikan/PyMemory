'''
    Imports
    Error handler
'''
import time
import math
sleep = lambda ms: time.sleep(ms/1000) # hehe

# i know that this is horrible practice,
# but stack traces can seem confusing to
# people without much experience
def memerr(func, err):
    print("[ERROR (%s)] %s" % (func, err))
    quit()

# yes i did in fact write this funciton
def meminfo(st):
    print("[INFO] %s" % (st))

# try to import ctypes and its siblings,
# it should never fail, but the school
# computers might have restrictions or something
try:
    import ctypes as ct
    from ctypes import wintypes as wt
    import subprocess, os
    import sys
except Exception as e:
    memerr("ImportError", str(e))

# what is the native byte order?
# essentially, are integer's stored
# left to right or right to left?
operating_byte_order = sys.byteorder

'''
    Some variable types for lookup
'''
C_types = {
    'int': { # int
        'size': 4,
        'convert': lambda b: int.from_bytes(b, operating_byte_order, signed = True),
        'bytes': lambda i: i.to_bytes(4, operating_byte_order)
    },
    'uint': { # unsigned int
        'size': 4,
        'convert': lambda b: int.from_bytes(b, operating_byte_order, signed = False),
        'bytes': lambda i: i.to_bytes(4, operating_byte_order)
    },
    'char': { # char
        'size': 1,
        'convert': lambda v: v.decode(), # this will error if the bytes aren't utf-8
        'bytes': lambda c: c.value.encode('utf-8')
    },
    'string': { # not technically a C_type but very useful (it is kind of `char[]`)
        'size': 4, # this must be changed to the length of the string
        'convert': lambda v: v.value.decode(), # this will error if the bytes aren't utf-8
        'bytes': lambda s: s.encode('utf-8')
    }
}

# a way to make sure that a vartype is valid
def ensure_vartype(funcname, vartype):
    # try to convert vartype
    if isinstance(vartype, str):
        if vartype in C_types:
            vartype = C_types[vartype]
    
    # confirm that this is a valid vartype
    if not isinstance(vartype, dict):
        memerr(funcname, 'vartype must be a dictionary, see winMemory.C_types["int"]')
    if not 'size' in vartype:
        memerr(funcname, 'vartype must contain "size", the size of the type in bytes')
    if not 'convert' in vartype:
        memerr(funcname, 'vartype must contain "convert", the function to convert a byte buffer to a python type')
    if not 'bytes' in vartype:
        memerr(funcname, 'vartype must contain "bytes", the function to convert a python type to a bytes instance')
    
    return vartype

'''
    Some stuff defined in C's <Windows.h> and <psapi.h> and <winnt.h>
'''

# process access rights
C_PROCESS_TERMINATE                  = 0x0001
C_PROCESS_CREATE_THREAD              = 0x0002
C_PROCESS_SET_SESSIONID              = 0x0004
C_PROCESS_VM_OPERATION               = 0x0008
C_PROCESS_VM_READ                    = 0x0010
C_PROCESS_VM_WRITE                   = 0x0020
C_PROCESS_DUP_HANDLE                 = 0x0040
C_PROCESS_CREATE_PROCESS             = 0x0080
C_PROCESS_SET_QUOTA                  = 0x0100
C_PROCESS_SET_INFORMATION            = 0x0200
C_PROCESS_QUERY_INFORMATION          = 0x0400
C_PROCESS_SUSPEND_RESUME             = 0x0800
C_PROCESS_QUERY_LIMITED_INFORMATION  = 0x1000
C_PROCESS_SET_LIMITED_INFORMATION    = 0x2000
C_SYNCHRONIZE                        = 0x00100000
C_STANDARD_RIGHTS_REQUIRED           = 0x000F0000
C_PROCESS_ALL_ACCESS                 = (C_STANDARD_RIGHTS_REQUIRED | C_SYNCHRONIZE | 0xFFFF)

# memory page access
C_PAGE_NOACCESS          = 0x01
C_PAGE_READONLY          = 0x02
C_PAGE_READWRITE         = 0x04
C_PAGE_WRITECOPY         = 0x08
C_PAGE_EXECUTE           = 0x10
C_PAGE_EXECUTE_READ      = 0x20
C_PAGE_EXECUTE_READWRITE = 0x40
C_PAGE_EXECUTE_WRITECOPY = 0x80
C_PAGE_GUARD             = 0x100
C_PAGE_NOCACHE           = 0x200

# memory page states
C_MEM_COMMIT             = 0x1000
C_MEM_RESERVE            = 0x2000
C_MEM_FREE               = 0x10000
C_MEM_PRIVATE            = 0x20000
C_MEM_MAPPED             = 0x40000
C_MEM_IMAGE              = 0x1000000

# T32Snapshot options
C_TH32CS_SNAPHEAPLIST = 0x00000001
C_TH32CS_SNAPPROCESS  = 0x00000002
C_TH32CS_SNAPTHREAD   = 0x00000004
C_TH32CS_SNAPMODULE   = 0x00000008
C_TH32CS_SNAPMODULE32 = 0x00000010
C_TH32CS_SNAPALL      = (C_TH32CS_SNAPHEAPLIST | C_TH32CS_SNAPPROCESS | C_TH32CS_SNAPTHREAD | C_TH32CS_SNAPMODULE)
C_TH32CS_INHERIT      = 0x80000000

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
    C function interfaces
    
    this code allows python to use
    functions that are written in
    the C programming language
'''
C_kernel32 = ct.WinDLL('kernel32', use_last_error = True)

C_open_process = C_kernel32.OpenProcess
C_open_process.argtypes = [wt.DWORD, wt.BOOL, wt.DWORD]
C_open_process.restype = wt.HANDLE

C_read_process_memory = C_kernel32.ReadProcessMemory
C_read_process_memory.argtypes = [wt.HANDLE, wt.LPCVOID, wt.LPVOID, ct.c_size_t, ct.POINTER(ct.c_size_t)]
C_read_process_memory.restype = wt.BOOL

C_get_module_information = ct.windll.psapi.GetModuleInformation
C_get_module_information.argtypes = [wt.HANDLE, wt.HMODULE, ct.POINTER(MODULEINFO), wt.DWORD]
C_get_module_information.restype = wt.BOOL

C_get_module_handle = C_kernel32.GetModuleHandleW
C_get_module_handle.argtypes = [wt.LPCWSTR]
C_get_module_handle.restype = wt.HMODULE

C_debug_active_process = C_kernel32.DebugActiveProcess
C_debug_active_process.argtypes = [wt.DWORD]
C_debug_active_process.restype = wt.BOOL

C_debug_active_process_stop = C_kernel32.DebugActiveProcessStop
C_debug_active_process_stop.argtypes = [wt.DWORD]
C_debug_active_process_stop.restype = wt.BOOL

C_virtual_query_ex = C_kernel32.VirtualQueryEx
C_virtual_query_ex.argtypes = [wt.HANDLE, wt.LPCVOID, ct.POINTER(MEMORY_BASIC_INFORMATION), ct.c_size_t]
C_virtual_query_ex.restype = ct.c_size_t

'''
    Main Class
'''
class Memory:
    # this constructor doesn't really do anything,
    # just makes an (optional) way save 1 line of code
    def __init__(self, process_name = None, process_id = None):
        self.process_handle = None
        self.process_id = None
        
        if process_id is not None:
            self.attach(process_id = process_id)
        elif process_name is not None:
            self.attach(process_name = process_name)
    
    def list_processes(self):
        os.system("tasklist")
        # should output a list of processes
        # example:
        # 
        # Image Name                     PID Session Name        Session#    Mem Usage
        # ========================= ======== ================ =========== ============
        # python.exe                    5544 Console                    2     11,272 K
        # other.exe                   123412 0123HelloWorld             0  6,969,420 K
    
    # exact same as above function except
    # return all module names instead of comparing
    def get_all_modules(self):
        module = C_kernel32.CreateToolhelp32Snapshot(C_TH32CS_SNAPMODULE | C_TH32CS_SNAPMODULE32, self.process_id)
        module_entry = MODULEENTRY32()
        module_entry.dwSize = ct.sizeof(module_entry)
        
        names = []
        while C_kernel32.Module32Next(module, ct.pointer(module_entry)):
            # add this one to the list
            names.append(module_entry.szModule.decode())
        
        return names
    
    # just print out `get_module_info` for each `get_all_modules`
    def list_modules(self):
        print()
        print(f"{'Module Name':<30}{'Memory Space':<42}")
        print("="*(42 + 30))
        for n in self.get_all_modules():
            try:
                info = self.get_module_info(n)
                print(f"{n:<30}[{hex(info['base']):>18} -> {hex(info['base'] + info['size']):<18}]")
            except:
                print(f"{n:<30}")
    
    # this funciton get's the base address of a module
    # that the process loaded... i think that's how it works?
    # i copy-paseted and converted this from a function that
    # i wrote years ago in C++
    def get_module(self, module_name):
        # really got no clue what these do
        module = C_kernel32.CreateToolhelp32Snapshot(C_TH32CS_SNAPMODULE | C_TH32CS_SNAPMODULE32, self.process_id)
        module_entry = MODULEENTRY32()
        module_entry.dwSize = ct.sizeof(module_entry)
        
        # loop through each loaded module,
        # and check if it's name matches what we want
        while C_kernel32.Module32Next(module, ct.pointer(module_entry)):
            if (module_entry.szModule.decode() == module_name):
                C_kernel32.CloseHandle(module)
                return module_entry.hModule
        
        # failure
        C_kernel32.CloseHandle(module)
        return False
    
    # this funciton gets information about a module
    # such as it's base address, it's size in memory
    # and it's entry point
    def get_module_info(self, module_name):
        # make sure we have a process
        if self.process_handle is None:
            memerr("get_module_info", "Memory must be attached to a process first!")
        
        # first, we must get a handle to the module
        module_handle = self.get_module(module_name)
        # make sure it's real
        if (module_handle is None) or (module_handle is False):
            memerr("x", "failed to get a handle to the module")
        
        # create an empty object to read into
        modinfo = MODULEINFO()
        
        # call the C function
        # it will return wether or not our call worked
        success = C_get_module_information(
            # the handle to the process
            self.process_handle,
            # the module we're getting info about
            module_handle,
            # a pointer to the modinfo we're reading into
            ct.byref(modinfo),
            # the size of that modinfo
            ct.sizeof(modinfo)
        )
        
        # ripperoni
        if not success:
            return False
        
        # return it in a dictionary for ease of access
        # also, now the user doesnt have to import ctypes
        information = {
            "base": modinfo.lpBaseOfDll,
            "size": modinfo.SizeOfImage,
            "entry": modinfo.EntryPoint
        }
        return information
    
    # this function just pauses execution of process
    def freeze(self):
        if self.process_id is None:
            memerr("freeze", "you must attach the process first")
        
        C_debug_active_process(self.process_id)
    
    # opposite of freeze
    def unfreeze(self):
        if self.process_id is None:
            memerr("unfreeze", "you must attach the process first")
            
        C_debug_active_process_stop(self.process_id)
    
    # this function allows python the access
    # to use ReadProccessMemory and WriteProcessMemory
    # by calling OpenProcess()
    def attach(self, process_name = None, process_id = None):
        # make sure we actually have something to attach to
        if (process_name is None) and (process_id is None):
            memerr("attach", "you must provide either a process_name or process_id")
        
        # if given a processid
        if process_id is not None:
            # make sure its a number
            if not isinstance(process_id, int):
                memerr("attach", "process_id must be an integer")
            self.process_id = process_id
            
            # just set the default error, this string probably wont be used
            err = "Failed to open process with PID of %d" % self.process_id
            
            # try to open the process id
            try:
                # not gonna lie, i copied this line from an old project
                # and i dont have internet access right now
                # so i don't know what the "False" does,
                # google "C OpenProcess arguments" to learn more
                self.process_handle = C_open_process(C_PROCESS_ALL_ACCESS, False, self.process_id)
            except Exception as e:
                self.process_handle = None
                err = str(e)
            
            # if the processid was invalid, then
            # C_open_process will return None
            if self.process_handle is None:
                memerr("attach", err)
            
            # notify success because: 
            #    - it's satisfying when something works
            #    - this function will only be called once
            #      so it's not like it's gonna hurt anyone
            meminfo("successfully attached to process with PID of %d" % (self.process_id))
            
        else: # if process_id was not given, but process_name was
            
            # make sure that process_name is a string
            if not isinstance(process_name, str):
                memerr("attach", "process_name must be a string")
            
            # should get reset by the try block
            # if it's not, we'll know it failed
            pid = None
            try:
                # see the `list_processes` function to see more about "tasklist"
                # call tasklist and filter by name
                out = subprocess.check_output('tasklist /FI "imagename eq %s"' % (process_name)).decode()
                
                # if the process was not found, then the above call will return:
                # "INFO: No tasks are running which match the specified criteria."
                # so we can just quickly chek if something was even returned
                assert (process_name in out), "process is not running"
                
                # the goal now is to find the processid in
                # the long jumbled string that `tasklist` returned
                # 
                # i dont know anything about regex in python,
                # and (again) i dont have internet, so i'm
                # just going to do this the bad way ...
                
                # firstly, find the position of the processname in the string
                start_pos = out.find(process_name)
                # and end position
                end_pos = start_pos + len(process_name)
                # anything after the process_name is fair game for PID
                # so we will cut away everything before and including it
                potential_pid = out[end_pos:]
                
                # the first number in the string will be the PID
                # so we'll just loop thru the characters in the string
                # and wait for the first number to begin then end
                found_number = False
                start = 0
                end   = 0
                for pos in range(len(potential_pid)):
                    character = potential_pid[pos]
                    if character.isnumeric(): # if char is 0 to 9
                        # if this is the first number
                        if not found_number:
                            start = pos
                            found_number = True
                        # if this is not the first number
                        # then we don't really need to do anything
                    else: # if char is not a number
                        if found_number: # if this char is the first char to not be a number
                            end = pos
                            break # we're done here :)
                
                # i dont know how this could happen,
                # but better safe then sorry
                assert found_number, "processid wasn't found"
                
                # slice our potential_pid from the start
                # of the pid to the end of it, this
                # is our PID in string form!
                pid = potential_pid[start:end]
                # and as a number
                pid = int(pid)
            except Exception as e:
                # if the tasklist command fails
                if "WinError" in str(e):
                    pid = 'Tasklist probably does not exist: "%s"' % (str(e))
                else: # if something else failed
                    pid = str(e)
            
            # again, shouldn't happen, but who knows
            if pid is None:
                pid = "failed to get processid from name"
            
            # if there was an error
            if isinstance(pid, str):
                memerr("attach", pid)
            
            # save the processid as a member to self
            self.process_id = pid
            
            # try to open the pid so we can access its memory
            try:
                self.process_handle = C_open_process(C_PROCESS_ALL_ACCESS, False, self.process_id)
            except:
                self.process_handle = None
            
            # make sure the OpenProcess worked
            if self.process_handle is None:
                memerr("attach", "Failed to open process %s with PID of %d" % (process_name, self.process_id))
            
            # notify success because: 
            #    - it's satisfying when something works
            #    - this function will only be called once
            #      so it's not like it's gonna hurt anyone
            meminfo("successfully attached to process %s with PID of %d" % (process_name, self.process_id))
    
    # some output while the program scans
    # just prints a progress bar and the number of addresses found
    def scan_progress(self, found_addresses = [], bytes_scanned = 0, bytes_total = 1, completed = False):
        percent_complete = bytes_scanned/bytes_total
    
        progress_bar_len = 20
        eqsigns = int(percent_complete * progress_bar_len)
        blanks = progress_bar_len - eqsigns
        pbar = "="*eqsigns + " "*blanks
        
        vispercent = str(((percent_complete * 1000) // 1) / 10)
        if not ('.' in vispercent):
            vispercent += ".0"
        while len(vispercent) < 5:
            vispercent = ' ' + vispercent
        print("%s%% [%s] -\t%d found - (%s / %s)" % (vispercent, pbar, len(found_addresses), hex(bytes_scanned), hex(bytes_total)), end = "\r")
        
        if completed:
            # scan complete, go to a new line in console
            print()
    
    # i'll comment this function later
    # sorry if i just screwed you over :(
    # the basic idea is to read large chunks of memory
    # then loop thru each address in that chunk and check
    # if it equals the value
    # i am writing this as of Feb. 9, 2020. so if you're in the future
    # then i'm probably never going to comment it, sorry
    def scan(self, value, vartype = 'int', scan_range = [0, 0x7ffffff00000], fast = True, callback = None, addresses = None):
        if callback is None:
            callback = self.scan_progress
    
        scan_type = ensure_vartype('scan', vartype)
        scan_binary = scan_type['bytes'](value)
        scan_size = len(scan_binary)
        scan_type['size'] = scan_size # only does anything when type is a string
        
        if addresses is not None:
            total_bytes = scan_size * len(addresses)
            scanned_bytes = 0
            addresses_found = []
            
            
            if callback:
                callback(found_addresses = addresses_found, bytes_scanned = scanned_bytes, bytes_total = total_bytes, completed = False)
            
            for address in addresses:
                if self.read(address, scan_type, bytes = True) == scan_binary:
                    addresses_found.append(address)
                scanned_bytes += scan_size
                
                if callback:
                    callback(found_addresses = addresses_found, bytes_scanned = scanned_bytes, bytes_total = total_bytes, completed = False)
            
            if callback:
                callback(found_addresses = addresses_found, bytes_scanned = scanned_bytes, bytes_total = total_bytes, completed = True)
            
            return addresses_found
        
        chunk = {'size': 1024, 'convert': lambda b: b, 'bytes': lambda b: b}
        
        found_addresses = []
        current_base = scan_range[0]
        while current_base < scan_range[1]:
            mbi = MEMORY_BASIC_INFORMATION()
            ret = C_virtual_query_ex(
                self.process_handle,
                wt.LPCVOID(current_base),
                ct.byref(mbi),
                ct.sizeof(mbi)
            )
            
            valid_mem = True
            if mbi.Protect is None:
                valid_mem = False
                
            if not((mbi.Protect & C_PAGE_READWRITE) or (mbi.Protect & C_PAGE_READONLY)):
                valid_mem = False
            
            if valid_mem:
                chunk['size'] = mbi.RegionSize
                binary = self.read(mbi.BaseAddress, chunk, bytes = True)
                
                for binary_begin in range(0, chunk['size'], (4 if fast else 1)):
                    read_binary = binary[binary_begin : binary_begin + scan_size]
                    if read_binary == scan_binary:
                        found_addresses.append(current_base + binary_begin)
            
            current_base += mbi.RegionSize
            if callback:
                callback(found_addresses = found_addresses, bytes_scanned = (current_base-scan_range[0]), bytes_total = (scan_range[1]-scan_range[0]), completed = False)
            
        if callback:
            callback(found_addresses = found_addresses, bytes_scanned = (scan_range[1]-scan_range[0]), bytes_total = (scan_range[1]-scan_range[0]), completed = True)
        return found_addresses
    
    def read(self, address, vartype = C_types['int'], bytes = False):
        # make sure that vartype is actually a vartype
        vartype = ensure_vartype('read', vartype)
        
        # confirm that we actually have the process open
        if self.process_handle is None:
            memerr('read', 'you must call attach to a process first (via attach())')
        
        # this is a place to store the memory that we read
        buffer = ct.create_string_buffer(vartype['size'])
        numbytesread = ct.c_ulonglong(0)
        
        # ReadProccessMemory will return wether
        # or not the call worked, the "success"
        success = C_read_process_memory(
            # this is the handle to the process, it's
            # what OpenProcess gave us when we asked
            # allowence to read/write the process's memory
            self.process_handle,
            # the memory address that we want to read
            # (it is being converted to a LPVOID)
            ct.c_void_p(address),
            # what variable should it read the data into
            buffer,
            # how many bytes to read
            # this should be the same as `vartype['size']`
            ct.sizeof(buffer),
            # this is a null pointer,
            # but i dont know why
            # look up "C ReadProcessMemory arguments"
            # to learn more
            ct.POINTER(ct.c_ulonglong)(numbytesread)
        )
        
        # if they want us to return the bytes, then allow it
        # by default we will convert it back
        if bytes:
            return bytearray(buffer) 
        else:
            return vartype['convert'](buffer)


'''
'''




























































