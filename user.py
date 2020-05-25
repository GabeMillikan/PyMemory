from pyMemory import memory

mem = memory(printErrors = True)
if mem.attach("chrome.exe"):
    print("Successfully attached with handle:", mem.hProcess)
else:
    print("Failed to attach")

print(mem.getModuleNames())

input("Press enter to quit")