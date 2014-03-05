
from .granule_filter import GranuleFilter

class PeriodicGranuleFilter(GranuleFilter):
    def __init__(self, input_config):
        GranuleFilter.__init__(self, input_config)
