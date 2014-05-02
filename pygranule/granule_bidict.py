
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
        
    def copy(self):
        base_copy = BiDict.copy(self)
        base_copy.gf_parent = self.gf_parent
        return base_copy

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

    def complete(self, **kwargs):
        """
        Expand the first item in this granule set,
        using the parent GranuleFilter to include all missing
        subsets and granules filling the AOI.
        I.e. turns an incomplete sampling into a complete set.
        """
        return self.gf_parent.complete(self.keys()[0], **kwargs)

    def completeness(self, **kwargs):
        """
        Evaluate fractional completion of this granule set
        with respect to the first item in this granule set.
        Returns a float, (1 - num. missing)/num when complete.
        """
        len_full = float( len( self.complete(**kwargs) ) )
        len_missing = float( len( self.missing(**kwargs) ) )
        return (len_full - len_missing)/len_full

    def missing(self, **kwargs):
        """
        Returns a BiDict of granules completing a pass
        w.r.t. the first item in this granule set.
        """
        return self.gf_parent.missing(self, **kwargs)

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
        return self


