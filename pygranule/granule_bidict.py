
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
        are implemented through callback to the parent granule filter.
        """
        BiDict.__init__(self, dictionary, bare)
        self.gf_parent = gf_parent
        
    def show(self):
        """
        Show this set of filepaths using
        the parent GranuleFilter.
        """
        self.gf_parent.show(self)
        return self

    def filter(self):
        """
        Filter this set of filepaths using
        the parent GranuleFilter.
        """
        return self.gf_parent(self)

    def split(self):
        """
        Split this set of filepaths into
        contiguous segments using
        the parent GranuleFilter.
        """
        return self.gf_parent.split(self)

    def fill_sampling(self, **kwargs):
        """
        Expand the first item in this granule set,
        using the parent GranuleFilter to include all missing
        subsets and granules filling the AOI.
        """
        return self.gf_parent.fill_sampling(self.keys()[0], **kwargs)

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
        


