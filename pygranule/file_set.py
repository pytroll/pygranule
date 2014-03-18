
import os

class FileSet(object):
    """
    A container for easy comparison of file paths,
    and file names.  For instance for quickly comparing files
    contained remotely and locally.
    """
    def __init__(self, paths=None):
        # store
        self.files = {}

        # isolate filename
        if paths is not None:
            for p in paths:
                self.files[os.path.basename(p)] = p

    def __str__(self):
        s=""
        for f in self.files:
            s += "   FILE:"+f + "    PATH:" + self.files[f] + "\n"
        return s

    def __iter__(self):
        return iter(self.files)

    def __iadd__(self,b):
        self.files.update( b.files )
        return self

    def copy(self):
        new_set = FileSet()
        new_set.files = self.files.copy()
        return new_set

    def paths(self):
        return self.files.values()

    def add(self,path):
        self.files[os.path.basename(path)] = path

    def remove(self, path):
        """
        Remove a path and its filename
        Path can be filename of full path.
        """
        del self.files[os.path.basename(path)]

    def has_file(self, filename):
        """
        Checks if filename is in this set.
        Can be a full path or just filename.
        Does not compare the path, only the basename.
        """
        if os.path.basename(filename) in self.files:
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
