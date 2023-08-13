from ctypes import *
from typing import Any
from types import MethodType

libc = CDLL("libc.so.6",use_errno=True)

FALLOC_FL_KEEP_SIZE      = 0x01
FALLOC_FL_PUNCH_HOLE     = 0x02
FALLOC_FL_COLLAPSE_RANGE = 0x08
FALLOC_FL_ZERO_RANGE     = 0x10
FALLOC_FL_INSERT_RANGE   = 0x20

try:
    fallocate = libc.fallocate64
    MAX_SIZE = 2**64
except:
    fallocate = libc.fallocate
    MAX_SIZE = 2**32

def hole(self, start:int, length:int):
    if self.closed:
        raise RuntimeError("The file has been closed.")
    fileno = self.fileno()
    result = fallocate(fileno, FALLOC_FL_PUNCH_HOLE | FALLOC_FL_KEEP_SIZE, start, length)
    errno = get_errno()
    if result == 0:
        return True
    raise OSError(errno = errno, strerror='Unable to deallocate space in file')    

def open_sparse(*args, **kwargs)->Any:    
    file = open(*args, **kwargs)
    if file.writable():
        # Linux does not need to mark a file sparse, we just make it sparse as we go.
        file.hole = MethodType(hole, file)
        return file
    file.close()
    raise RuntimeError('File not opened as writeable.')
