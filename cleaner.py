
import mmap
import random
import struct
import os
import platform
import ctypes

def getFreeSpace(folder):
    """ Return folder/drive free space (in bytes)
    """
    if platform.system() == 'Windows':
        free_bytes = ctypes.c_ulonglong(0)
        ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p(folder), None, None, ctypes.pointer(free_bytes))
        return free_bytes.value
    else:
        return os.statvfs(folder).f_bavail * os.statvfs(folder).f_bsize

def cleanDiskSpace(Path):
    try:
        FREESPACE = getFreeSpace(Path) - 1048576 * 10

        FILESIZE              = 1048576 * 1024
        BLOCKSIZE             = 8388608#1048576 * 8
        BLOCKSCOUNT           = int(FILESIZE / BLOCKSIZE) - 1# + (1 if FILESIZE % BLOCKSIZE != 0 else 0)
        RANDOMDATABLOCKSCOUNT = 2
        LISTOFBLOCKS          = list(i for i in range(BLOCKSCOUNT))
        BYTESLIST             = []

        for i in range(RANDOMDATABLOCKSCOUNT):
            batemplate = bytearray(random.getrandbits(8) for i in range(int(BLOCKSIZE/1024)))
            ba = batemplate.copy()
            for i in range(1024):
                ba += batemplate
            BYTESLIST.append(ba)

        fileIndex = 1
        files = []
        while FREESPACE > FILESIZE:
            random.shuffle(LISTOFBLOCKS)

            fileName = Path + "job" + str(fileIndex)
            file = open(fileName, "wb")
            file.truncate(FILESIZE)
            file.flush()
            file.close()
            file = open(fileName, "r+b")
    
            files.append(fileName)

            mm = mmap.mmap(file.fileno(), 0)

            randomBlock = 0
            for i in LISTOFBLOCKS:
                mm.seek(i * BLOCKSIZE)
                mm.write(BYTESLIST[randomBlock])
                randomBlock += 1
                if randomBlock == RANDOMDATABLOCKSCOUNT: randomBlock = 0
    
            mm.flush()
            mm.close()
            file.close()
    
            fileIndex += 1
            FREESPACE -= FILESIZE
 
        for fileName in files:
            os.remove(fileName)
    except Exception:
        pass