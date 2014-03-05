

from .granule_filter import GranuleFilter
from .pyorbital_layer import PyOrbitalLayer

class OrbitalGranuleFilter(GranuleFilter):
    def __init__(self, input_config):
        GranuleFilter.__init__(self, input_config)
        # instanciate orbital layer
        aoi = self.get_aoi()
        sat = self._validated_config("sat_name")
        self.orbital_layer = PyOrbitalLayer(aoi,sat)

    def check_sampling_from_time(self, start, period=None):
        """
        Tests if granule at time step start samples (overlaps) target
        point / area of interest.
        """
        if period is None:
            period = self.get_time_step().total_seconds()/60.0
        
        return self.orbital_layer.does_swath_sample_aoi(start,period)

