'''
    proc.py is the API on the process side of file-system calls.
'''

from pfs import *


class PerProcessFileEntry:
    '''
        this is the data structure for the per-process open-file table.
        It contains a reference to the system-wide open-file table,
        plus additional state, including the position.
    '''
    def __init__(self, fcb):
        self.fcb = fcb
        self.pos = 0  # the logical position (block) of the "file head"

class ProcessFS:
    def __init__(self, fs, homePath):
        self.openFileTable  = [ ]  # list of references to system-wide OFT
        self.homePath= homePath
        self.fs = fs
        self.cwd, filename = self.fs.parsePath(homePath, None)


    def open(self, filepath):
        '''
            open a file by name, read its FCB into in-memory open-file table
            add to the system-wide open file table. return file descriptor,
            which is index into per-process open file table.
            set file-head to zero
        '''
        # the caller provides path including directory to file.
        # parse to get directory reference and file name.
        enclosingDir, filename = self.fs.parsePath(filepath, self.cwd)

        # find the FCB under the given file name in the enclsoing dir
        # if not found or not file, raise exception.

        # if the FCB is not already in the system-wide open file table,
        # then add it, and increment its open count.

        # create a per-process file entry for this FCB,
        # put it in the per-process open file table, 
        # and set the descriptor (an int) to be its index in the table.
        # update the last-access time
        # return the descriptor.


    def close(self, descriptor):
        '''
            removes the entry in the per-process open-file table,
            decrement the count in system-wide open-file table entry,
            if count zero 
               remove entry in system-wide table
               update metadata to disk-based directory structure
        '''
        # find the per-process file entry using descriptor
        # extract the FCB, decrement its open count
        # if no more open count, delete its entry in the system-wide 
        #   open-file table.
        # clear its per-process open file entry.


    def read(self, descriptor, nBlocks=1):
        '''
            read the file starting from current block for nBlocks
            increment the file-head by nBlocks
            return the data read
        '''
        # find the per-process file entry using descriptor
        # get the file-head position and FCB
        # (assume file-head points at the block to read)
        # read one block at a time up to either nBlocks or end of file
        #     based on the logical-to-physical mapping
        # increment the file head, append the data to the return value var
        # update the last access time
        # return the data


    def write(self, descriptor, data):
        '''
            write the file sequentially for nblocks from the file head position,
            by extending file if necessary.
            for simulation, data is a list of strings, 
            where each string is the content for one block.
            so len(data) is the number of blocks
        '''
        # find the per-process file entry
        # extract the position, FCB, and logical-to-physical index
        # check if we need to allocate more blocks
        # if enough, add the newly allocated ones to the end of the file
        #    (hint: by extending the index)
        # but if not enough, raise an exception
        # write one block at a time from current head position
        # increment file head position for each block written
        # update the last-modification time.




if __name__ == '__main__':
    directoryTree = ( '/',  ('home/', ('u1/', 'hello.c'),
                                    ('u2/', 'world.h'), 'homefiles'),
                            ('bin/', 'ls'),
                            ('etc/', ))

    # make an initial directory
    print('input directory tree=%s' % repr(directoryTree))

    fs = PFS(nBlocks = 16)
    root = MakeFSFromTree(fs, directoryTree)
    print('tuple reconstructed from directory=%s' % repr(MakeTreeFromDir(root)))
    print('creation time for /home/u1/hello.c is %s' % \
            root.lookup('home').lookup('u1').lookup('hello.c').createTime)



    p1 = ProcessFS(fs, '/home/u1')
    p2 = ProcessFS(fs, '/home/u2')

    # print out directory

    f1 = p1.open('hello.c')
    p1.write(f1, ['hello', 'world'])
    f2 = p2.open('/home/u1/hello.c')
    print('f2 read=%s' % p2.read(f2))
    print('f2 read=%s' % p2.read(f2))