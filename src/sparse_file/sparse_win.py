from ctypes import *
from msvcrt import get_osfhandle
from typing import Any
from types import MethodType

FSCTL_SET_ZERO_DATA = 0X980C8
FSCTL_SET_SPARSE = 0X900C4

NO_ERROR = 0
INVALID_FILE_SIZE = 4294967295

DeviceIoControl=windll.kernel32.DeviceIoControl
DeviceIoControl.restype = c_bool

GetCompressedFileSizeW = windll.kernel32.GetCompressedFileSizeW
GetFinalPathNameByHandleW = windll.kernel32.GetFinalPathNameByHandleW


class FILE_ZERO_DATA_INFORMATION(Structure):
    _fields_ = [("FileOffset",c_longlong),("BeyondFinalZero",c_longlong)]

def set_file_as_sparse(file:Any):
    handle = get_osfhandle(file.fileno())
    dwTemp = c_long()
    result = DeviceIoControl(handle, FSCTL_SET_SPARSE, None, 0, None, 0, byref(dwTemp), None)
    if not result:
        raise WinError()
    return True

def hole(self, start:int, length:int):
    if self.closed:
        raise RuntimeError("The file has been closed.")
    fileno = self.fileno()
    handle = get_osfhandle(fileno)
    fs = FILE_ZERO_DATA_INFORMATION()
    fs.FileOffset = start
    fs.BeyondFinalZero = start + length
    dwTemp = c_long()
    result = DeviceIoControl(handle, FSCTL_SET_ZERO_DATA, pointer(fs), sizeof(fs), None, 0, byref(dwTemp), None)
    if result:
        self.flush()
        return True
    raise WinError()

def size_on_disk(self):
    if self.closed:
        raise RuntimeError("The file has been closed.")
    fileno = self.fileno()
    handle = get_osfhandle(fileno)
    filename = create_unicode_buffer(2048)
    filename_length = GetFinalPathNameByHandleW(handle, filename, len(filename), 0)
    if filename_length > 0:
        hi_dword = c_long()
        lo_dword = GetCompressedFileSizeW(filename, byref(hi_dword))
        last_error = GetLastError()
        if lo_dword != INVALID_FILE_SIZE or last_error == NO_ERROR:
            return hi_dword.value * 0x100000000 + lo_dword
    raise WinError()

def open_sparse(*arg, **kwarg)->Any:
    file = open(*arg, **kwarg)
    if file.writable():
        set_file_as_sparse(file)
        file.hole = MethodType(hole, file)
        file.size_on_disk = MethodType(size_on_disk, file)
        return file
    file.close()
    raise RuntimeError('File not opened as writeable.')

