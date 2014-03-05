
from datetime import datetime



class FileNameParser(object):
    """
    This module takes care of checking if satellite granule
    filenames match a particular pattern, including granule subsetting.
    The module can validate a proposed file name, but also extract
    time stamps and subset name from the file name.

    Note: The module does not validate the time stamp itself,
    its granulation step or area of interest intersect.
    """
    def __init__(self,file_name_pattern, subsets=None):
        self.pattern = file_name_pattern
        if subsets is None:
            self.subsets = {}
        else:
            self.subsets = _dict_subset_expression(subsets)
            
    def filenames_from_time(self,t):
        """ 
        Creates a list of legal filenames from the file path pattern, subset names,
        given a single datetime stamp.
        If time stamp does not match granulation and offset, then an empty
        list is returned.
        If granule does not cover targets zone, then an empty list is returned.
        """
        # apply datetime formatting
        pattern_w_t = t.strftime(self.pattern)

        # apply subset filename expansion
        if self.subsets is None:
            paths = [pattern_w_t]
        else:
            paths = [ x[0] for x in _subset_filename_expansion(pattern_w_t, self.subsets) ]
            
        return paths

    def time_from_filename(self, filename):
        """
        Attempt to extract a datetime from filename.
        Returns datetime if successful, else None.
        """
        # extract subset patterns
        subset_patterns = [ x[0] for x in _subset_filename_expansion(self.pattern,self.subsets) ]

        # try to extract a datetime
        for p in subset_patterns:
            try:
                t = datetime.strptime(filename, p)
                return t
            except ValueError:
                continue
        return None

    def validate_filename(self, filename):
        """
        Check if input file name matches the file name pattern
        Returns True of False.
        """
        if self.time_from_filename(filename) is None:
            return False
        else:
            return True

    def subset_from_filename(self, filename):
        """
        Attempt to extract a subset from filename.
        Returns tuple of subset names if filename is valid, 
        else throw ValueError.
        """
        if self.validate_filename(filename):
            pattern_w_t = self.time_from_filename(filename).strftime(self.pattern)
            if self.subsets is None:
                return ()
            else:
                paths = _subset_filename_expansion(pattern_w_t, self.subsets)
                for i,p in enumerate(paths):
                    if filename == p[0]:
                        return p[1]
            
        else:
            raise ValueError("Invalid filename -> No subset extracted")

def _subset_filename_expansion(pattern, subset, values=()):
    """ helper function for expanding subset filenames into filename path pattern 
-- input argument values should NOT be used by caller (recursive argument) """
    if len(subset)>0:
        L = []
        for key in subset:
            L = L + _subset_filename_expansion(pattern, subset[key],values+(key,))
        return L
    else:
        # pad up missing values
        for i in range(pattern.count("{")-len(values)):
            values = values+("",)
        # format pattern
        return [(pattern.format(*values),values)]

def _expand_subset_expression(s):
    s = _expand_doubledot(s)
    return s
            
def _expand_doubledot(s):
    """ expands subset expressions such as "1..4", to enumerated representation 1,2,3,4 """
    if '..' in s:
        splt = s.split('..')
        if len(splt) == 2:
            if splt[0].isdigit() and splt[1].isdigit():
                ns = ""
                for i in range(int(splt[0]),int(splt[1])+1):
                    ns += (str(i) + ',')
                return ns.strip(',')
    return s

def _dict_subset_expression(s):
    if len(s)>2:
        s = s[1:-1] # stripping outer braces
        s = _expand_subset_expression(s) # expand patterns, eg 1..3 = 1,2,3
        subs = _comma_split(s)
        d = {}
        for sub in subs:
            if ':' in sub:
                idx = sub.find(':')
                key = sub[:idx].strip()
                stub = sub[idx+1:]
            else:
                key = sub
                stub = ""
            d[key]=_dict_subset_expression(stub)
        return d
    else:
        return {}

def _comma_split(s):
    level=0
    splt = []
    start_i = 0
    for i in range(len(s)):
        if s[i] == '{':
            level += 1
        elif s[i] == '}':
            level -= 1
        if s[i] == ',' and level == 0:
            splt.append(s[start_i:i])
            start_i=i+1
    splt.append(s[start_i:len(s)])
    return splt
     
def _is_balanced_braces(s, n_open=0):
    """ helper function to check if { braces are balanced """
    # next braces
    o = s.find('{')
    c = s.find('}')
    if n_open < 0:
        return False
    elif o<0: # no more open
        if c<0: # no more closed
            if n_open == 0:
                return True
            else:
                return False
        else: # another closed
            return _is_balanced_braces(s[c+1:], n_open - 1)
    else: # another open
        if c<0: # but no more closed
            return False
        elif c<o: #closed is earlier than open
            return _is_balanced_braces(s[c+1:], n_open - 1)
        else: # open is first
            return _is_balanced_braces(s[o+1:], n_open + 1)
