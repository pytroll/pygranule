
from .bidict import BiDict


class FileTransferBiDict(BiDict):
    """
    An extension to the bi-directional dictionary class
    used for associating source and destination file name paths. 
    Furthermore allows for file transfer is FileAccessLayer 
    object is provided.
    """
    def __init__(self, dictionary=None, file_access_layer=None, bare=False):
        BiDict.__init__(self, dictionary, bare)
        self.file_access_layer = file_access_layer
        
    def transfer(self):
        """
        Execute file transfer from source file system 
        to destination file system, defined by the 
        file_access_layer, see instantiation. 
        Throws an AttributeError, when no file_access_layer
        has been defined or aggregated by the user.
        """
        for key in self.fwd:
            self.file_access_layer.copy_file(key, self.fwd[key])
        


