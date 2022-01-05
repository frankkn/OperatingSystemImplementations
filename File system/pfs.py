'''
    pfs.py is a toy file system in python.
'''

# from typing_extensions import runtime
from typing import Union
from cntlblks import *

class PFS:
    def __init__(self, nBlocks=16, nDirs=32, nFCBs=64):
        '''
            nBlocks is an int for the number of blocks in this file system (for user)
            root is the directory control block of the root and
            has the link to some initial directories.
        '''
        # - on-disk structure, assuming one partition:
        #   - list of directory control blocks (more like a tree)
        #   - list of file control blocks
        self.nBlocks = nBlocks

        self.FCBs = [ ] # file control blocks
        self.freeBlockSet = set(range(nBlocks))
        self.freeDEntrys = [DEntry() for i in range(nDirs)]
        self.freeFCBs = [FCB() for i in range(nFCBs)]

        self.root = self.allocDEntry()

        # - in-memory structure
        #   - in-memory directory structure
        #   - system-wide open file table
        #   - per-process open file table
        self.sysOpenFileTable = []
        self.sysOpenFileCount = []

        self.storage = [None for i in range(nBlocks)]  # physical storage


    def allocFCB(self):
        f = self.freeFCBs.pop()
        FCB.__init__(f)
        return f

    def freeFCB(self, f):
        self.freeFCBs.append(f)

    def allocDEntry(self):
        d = self.freeDEntrys.pop() # recycle
        DEntry.__init__(d)  # start fresh
        return d

    def freeDEntry(self, d):
        self.freeDEntrys.append(d)

    def parsePath(self, path, defaultDir):
        '''
            utility function to convert from file path (absolute or relative)
            to (DEntry, filename).
            If no directory is specified, then the current working directory
            is returned; filename may be None if empty string.
        '''
        t = path.split('/') # 以/為分隔符，分隔t的內容
        d = self.root
        filename = ''  # by default, name is empty
        if len(t) == 1:
            # no slash = use defaultDir
            d = defaultDir
            return d, t[0]
        elif len(t) > 1:
            # at least we have a slash
            if t[0] == '':
                # start from root
                d = self.root
            else: # relative to current directory
                d = defaultDir.lookup(t[0])
            # remove trailing / if there is one
            if t[-1] == '':
                filename = t.pop()
            for i, n in enumerate(t[1:]):
                member = d.lookup(n)
                if member is None:
                    filename = n
                    break
                if isinstance(member, DEntry):
                    # keep going
                    d = member
                    continue
                if isinstance(member, FCB):
                    # this must be the last
                    if i == len(t[1:]) - 1:
                        filename = n
                        break
                raise ValueError('%s is not a directory' % n)
            # now d points to the directory
            return (d, filename)
        else: # len(t) < 1: not possible
            raise ValueError('split error on %s' % path)

    def createFile(self, name, enclosingDir):
        # @@@ write your code here
        # allocate a new FCB and update its directory structure:
        # * if default directory is None, set it to root.
        if enclosingDir is None:
            enclosingDir = self.root
        # * if name already exists, raise exception
        if name in enclosingDir.names:
            raise RuntimeError("The file name has already existed")
        # * allocate a new FCB, add it to the enclosing dir by name,
        fcb = self.allocFCB()
        enclosingDir.addFile(fcb, name)
        # * append to the FCB list of the file system.
        self.FCBs.append(fcb)
        # Note: this does not allocate blocks for the file.

    def createDir(self, name, enclosingDir):
        # @@@ write your code here
        # create a new directory under name in enclosing directory.
        if enclosingDir is None:
            enclosingDir = self.root
        # * check if name already exists; if so, raise exception.
        if name in enclosingDir.names:
            raise RuntimeError("The file name has already existed")
        # * allocate a DEntry, add it to enclosing directory,
        dEntry = self.allocDEntry()
        enclosingDir.addDir(dEntry, name)
        # * return the new DEntry.
        return dEntry


    def deleteFile(self, name, enclosingDir):
        # @@@ write your code here
        # * lookup the fcb by name in the enclosing directory.
        fcb = enclosingDir.lookup(name)
        if fcb is not None:
        # * if linkCount is 1 (which means about to be 0 after delete)        
        #   and the file is still opened by others, then
        #   raise an exception about unable to delete open files.
            if fcb.linkCount == 1 and fcb.openCount > 0:
                raise RuntimeError("This file is opened")
        # * call rmFile on enclosingDir to remove the fcb (and name).
            enclosingDir.rmFile(fcb)
        # * if no more linkCount, then
            if fcb.linkCount == 0: 
        #   * recycle free the blocks.
        #   * recycle the fcb
                if fcb in self.FCBs:
                    self.FCBs.remove(fcb)
                    self.freeFCB(fcb)

    def deleteDirectory(self, name, enclosingDir):
        # @@@ write your code here
        # * lookup the dentry by name in the enclosing directory.
        dEntry = enclosingDir.lookup(name)
        if len(dEntry.content) != 0:
        # * if the directory is not empty, raise exception about
            raise RuntimeError("This directory is not empty")
        #   unable to delete nonempty directory.
        # * call rmDir on enclosing directory
        enclosingDir.rmDir(dEntry)
        # * recycle the dentry
        self.freeDEntry(dEntry)

    def rename(self, name, newName, enclosingDir):
        # @@@ write your code here
        # * check if newName is already in enclosingDir, raise exception
        if newName in enclosingDir.names:
            raise RuntimeError("The new name has already existed")
        # * find position of name in names list of enclosingDir
        # * change the name to newName in that list
        enclosingDir.names[enclosingDir.names.index(name)] = newName
        # * set last modification time of enclosing directory
        enclosingDir.updateModTime()

    def move(self, name, fromDir, toDir):
        # @@@ write your code here
        # * check if name is already in toDir, raise exception
        if name in toDir.names:
            raise RuntimeError("name is already in toDir")
        # * lookup name and see if it is directory or file.
        control_block = fromDir.lookup(name)
        
        # * if directory, remove it from fromDir (by calling rmDir),
        if isinstance(control_block, DEntry):
            fromDir.rmDir(control_block)
        #   add it to toDir (by calling addDir)
            toDir.addDir(control_block, name)
        # * if file, remove it from fromDir (by calling rmFile)
        if isinstance(control_block, FCB):
            fromDir.rmFile(control_block)
        #   add it to toDir (by calling addFile)
            toDir.addFile(control_block, name)
    
    def allocateBlocks(self, nBlocksToAllocate):
        # allocates free blocks from the pool and return the set of
        # block numbers 
        # * if there are not enough blocks, then return None
        if len(self.freeBlockSet) < nBlocksToAllocate:
            return None
        # * find S = nBlocksToAllocate members from the free set
        S = set()
        for _ in range(nBlocksToAllocate): 
            x = next(iter(self.freeBlockSet))
            S.add(x)
            self.freeBlockSet.remove(x)
        # * remove S from the free set
        # * return S
        return S

    def freeBlocks(self, blocksToFree):
        # blocksToFree is the set of block numbers as returned from
        # allocateBlocks().
        # * set the free set to union with the blocksToFree.
        self.freeBlockSet |= blocksToFree
        # * strictly speaking, those blocks should also be erased.

def MakeFSFromTree(fs, tree, root=None):
    '''
        utility function to make directory from tree
    '''
    if tree == ():
        return None
    if isinstance(tree, str):
        fs.createFile(name=tree, enclosingDir=root)
    elif tree[0][-1] == '/':
        if root is None:
            c = fs.root
            root = c
        else:
            # c = root.makeDir(tree[0][:-1])
            name = tree[0][:-1]
            c = fs.createDir(name, enclosingDir=root)
        if len(tree) > 1:
            for t in tree[1:]:
                MakeFSFromTree(fs, t, c)
    return root


    
def testBlockAlloc(fs):
    print('freeblocks=%s' % fs.freeBlockSet)
    a = fs.allocateBlocks(5)
    b = fs.allocateBlocks(3)
    c = fs.allocateBlocks(2)
    d = fs.allocateBlocks(1)
    e = fs.allocateBlocks(4)
    print('allocate (5)a=%s, (3)b=%s, (2)c=%s, (1)d=%s, (4)e=%s' % (a,b,c,d,e))
    print('freeBlockSet=%s' % fs.freeBlockSet)
    fs.freeBlocks(b)
    print('after freeBlocks(%s), freeBlockSet=%s' % (b, fs.freeBlockSet))
    fs.freeBlocks(d)
    print('after freeBlocks(%s), freeBlockSet=%s' % (d, fs.freeBlockSet))
    f = fs.allocateBlocks(4)
    print('after allocateBlocks(4)=%s, freeBlockSet=%s' % (f, fs.freeBlockSet))
    fs.freeBlocks(a | c)
    print('after freeBlocks(a|c)=%s, freeBlockSet=%s' % (a|c, fs.freeBlockSet))


if __name__ == '__main__':
    directoryTree = ( '/',  ('home/', ('u1/', 'hello.c', 'myfriend.h'),
                                    ('u2/', 'world.h'), 'homefiles'),
                            ('bin/', 'ls'),
                            ('etc/', ))

    # make an initial directory
    print('input directory tree=%s' % repr(directoryTree))

    fs = PFS(nBlocks = 16)
    """
    root = MakeFSFromTree(fs, directoryTree)
    print('directory=%s' % repr(MakeTreeFromDir(root)))
    d, f = fs.parsePath('/home/u1/', root)
    print('last modification date for /home/u1/ is %s' %  d.modTime)
    time.sleep(2)
    fs.rename('hello.c', 'goodbye.py', d)
    print('after renaming=%s' % repr(MakeTreeFromDir(root)))
    print('last modification date for /home/u1/ is %s' %  d.modTime)
    t, f = fs.parsePath('/home/u2/', root)
    fs.move('myfriend.h', d, t) # from /home/u1 to /home/u2
    print('after moving=%s' % repr(MakeTreeFromDir(root)))
    fs.move('etc', root, d)  # move /etc to /home/u1
    print('after moving=%s' % repr(MakeTreeFromDir(root)))
    """
    testBlockAlloc(fs)