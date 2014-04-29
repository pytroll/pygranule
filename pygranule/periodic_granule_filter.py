
from .granule_filter import GranuleFilter
from .granule_bidict import GranuleBiDict

class PeriodicGranuleFilter(GranuleFilter):

    __implements__ = (GranuleFilter,)

    def __init__(self, input_config):
        GranuleFilter.__init__(self, input_config)

    def check_sampling_from_time(self, start, period=None):
        """
        Tests if granule at time step start samples (overlaps) target
        point / area of interest. For periodic filters, this is always
        true.
        """
        return True

    def show(self, filepaths):
        """
        If provided, shows an image for the area extent of the granules,
        and the target area. Not implemented for PeriodicGranuleFilter.
        """
        raise NotImplementedError

    def split(self, filepaths):
        """
        Separates a list of input file paths into 
        chunks. File paths must have a valid file name pattern.
        Return result as list of GranuleBiDicts.
        Note: Opeartion does not pre-perform filtering.
        """
        print "UNIMPELMENTED: should split into BiDicts of same"
        print "time stamp"
        

    def fill_sampling(self, filepath):
        """
        Given a valid filepath, returns full set of filepaths 
        that complete this periodic sampling.
        """
        t = self.source_file_name_parser.time_from_filename(filepath)
        full_sample = self.source_file_name_parser.filenames_from_time(t)
        # return result as GranuleBiDict
        return self.translate(full_sample)
        
