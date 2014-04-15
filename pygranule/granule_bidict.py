
from .bidict import BiDict


class GranuleBiDict(BiDict):
    """
    An extension to the bi-directional dictionary class
    used for associating source and destination file name paths. 
    Furthermore allows for file transfer is FileAccessLayer 
    object is provided.
    """
    def __init__(self, dictionary=None, bare=False, gf_parent=None):
        """
        Extension to bidict, holding a reference to its
        GranuleFilter parent object.
        Additional routines, such as plot, and file transfer
        are implemented through the parent.
        """
        BiDict.__init__(self, dictionary, bare)
        self.gf_parent = gf_parent
        
    def show(self):
        self.gf_parent.show(self)

    def transfer(self):
        """
        Execute file transfer from source file system 
        to destination file system, defined by the 
        file_access_layer, see instantiation. 
        Throws an AttributeError, when no file_access_layer
        has been defined or aggregated by the user.
        """
        for key in self.fwd:
            self.gf_parent.file_access_layer.copy_file(key, self.fwd[key])
        


