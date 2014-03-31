
from .granule_filter import GranuleFilter

class PeriodicGranuleFilter(GranuleFilter):
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
