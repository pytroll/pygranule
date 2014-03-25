

def reverse_dictionary(d):
    rev_d = {}
    for key in d:
        val = d[key]
        rev_d[val] = key
    return rev_d

class BiDict(object):
    """
    Bidirectional dictionary.
    Allows inverse listings, value -> key
    as well as usual key -> value.
    Only supports one to one mapping,
    i.e. unique keys and unique values.
    """
    def __init__(self,dictionary=None, bare=False):
	if dictionary is not None:
            self.fwd = dictionary
            self.bwd = reverse_dictionary(self.fwd)
        elif bare == True:
            pass
        else:
            self.fwd = {}
            self.bwd = {}

    def __str__(self):
        return str(self.fwd)

    def __getitem__(self, key):
        return self.fwd[key]

    def __setitem__(self, key, value):
        self.fwd[key] = value
        self.bwd[value] = key
    
    def __delitem__(self, key):
        self.remove(key)

    def __invert__(self):
        return self.inverse()

    def __iter__(self):
        return iter(self.fwd)

    def __iadd__(self,other):
        self.fwd.update(other.fwd)
        self.bwd.update(other.bwd)
        return self

    def copy(self):
        new = self.__class__(bare=True)
        new.fwd = self.fwd.copy()
        new.bwd = self.bwd.copy()
        return new

    def inverse(self):
        new = self.__class__(bare=True)
        new.fwd = self.bwd
        new.bwd = self.fwd
        return new

    def remove(self, key):
        val = self.fwd[key]
        del self.bwd[val]
        del self.fwd[key]

    def reduce(self, external_dict):
        """
        Removes those keys and values that correspond
        to the keys in the external dict-like object.
        Note that the values may differ in this and 
        external dict object may differ.
        """
        for key in external_dict:
            if key in self.fwd:
                del self.bwd[self.fwd[key]]
                del self.fwd[key]

    def update(self, external_dict):
        """
        Updates this BiDict with any corresponding or new key/values
        found in the external dict-like object. 
        """
        for key in external_dict:
            if key in self.fwd:
                # update the forward dict record
                new_val = external_dict[key]
                old_val = self.fwd[key]
                self.fwd[key] = new_val
                # remove reverse dict record
                del self.bwd[old_val]
                # and add the new one
                self.bwd[new_val] = key
            else:
                self.fwd[key] = external_dict[key]
                self.bwd[self.fwd[key]] = key

    def difference(self, external_dict):
        """
        Return a BiDict containing all missing
        key-values in the external dict-like object.
        """
        new_dict = self.copy()
        for key in external_dict:
            if key in new_dict:
                del new_dict[key]
        return new_dict



