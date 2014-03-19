
import os

class FileSet(object):
    """
    A container for easy comparison of file paths,
    and file names. E.g. for quickly comparing files
    contained remotely and locally.
    """
    def __init__(self, paths=None):
        # store
        self.filedict = {}

        # isolate filename
        if paths is not None:
            for p in paths:
                self.filedict[os.path.basename(p)] = p

    def __str__(self):
        s=""
        for f in self.filedict:
            s += "   FILE:"+f + "    PATH:" + str(self.filedict[f]) + "\n"
        return s

    def __getitem__(self,key):
        return self.filedict[key]

    def __iter__(self):
        return iter(self.filedict)

    def __iadd__(self,b):
        self.filedict.update( b.filedict )
        return self

    def copy(self):
        new_set = FileSet()
        new_set.filedict = self.filedict.copy()
        return new_set

    def files(self):
        return self.filedict.keys()

    def paths(self):
        return self.filedict.values()

    def add(self,path):
        self.filedict[os.path.basename(path)] = path

    def remove(self, path):
        """
        Remove a path and its filename
        Path can be filename of full path.
        """
        del self.filedict[os.path.basename(path)]

    def has_file(self, filename):
        """
        Checks if filename is in this set.
        Can be a full path or just filename.
        Does not compare the path, only the basename.
        """
        if os.path.basename(filename) in self.filedict:
            return True
        else:
            return False

    def difference(self, input_set):
        """
        Compares this set with input granule_set and returns
        a new granule set comprising those files that are not
        in the input set. The full path will be according to this
        granule set. 
        """
        new_set = self.copy()
        for f in input_set:
            if f in new_set:
                new_set.remove(f)
        return new_set
