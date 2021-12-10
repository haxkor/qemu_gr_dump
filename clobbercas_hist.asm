warning: Error disabling address space randomization: Operation not permitted
Histogram: Calling MapReduce Scheduler
Exception ignored on calling ctypes callback function: <bound method Uc._hook_intr_cb of <unicorn.unicorn.Uc object at 0xfffee8286af0>>
Traceback (most recent call last):
  File "/usr/local/lib/python3.9/dist-packages/unicorn/unicorn.py", line 495, in _hook_intr_cb
    cb(self, intno, data)
  File "/git_stuff/pwndbg/pwndbg/emu/emulator.py", line 266, in hook_intr
    debug("Got an interrupt")
TypeError: debug() missing 1 required positional argument: 'args'
