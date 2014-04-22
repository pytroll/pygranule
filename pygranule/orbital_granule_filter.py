

from .granule_filter import GranuleFilter, GranuleFilterError
from .pyorbital_layer import PyOrbitalLayer

class OrbitalGranuleFilter(GranuleFilter):
    
    __implements__ = (GranuleFilter,)

    def __init__(self, input_config):
        GranuleFilter.__init__(self, input_config)
        # instanciate orbital layer
        aoi = self.get_aoi()
        sat = self.config["sat_name"]
        ins = self.config["instrument"]
        self.orbital_layer = PyOrbitalLayer(aoi, sat, instrument=ins)

    def check_sampling_from_time(self, start, period=None):
        """
        Tests if granule at time step start samples (overlaps) target
        point / area of interest.
        """
        if period is None:
            period = self.get_time_step().total_seconds()/60.0
        
        return self.orbital_layer.does_swath_sample_aoi(start,period)

    def show(self, filepaths):
        """
        Shows an image for the area extent of the granules,
        and the target area.
        """
        dt = self.get_time_step()
        t = []
        for f in filepaths:
            t.append(self.source_file_name_parser.time_from_filename(f))
        
        # select plotting routine depending if 
        # pycoast version has add_polygon
        try:
            from pycoast import ContourWriterAGG
            if hasattr( ContourWriterAGG, 'add_polygon'):
                self.orbital_layer.show_swath_pycoast(t, period=dt.total_seconds()/60.0)
            else:
                raise ImportError
        except ImportError:
            self.orbital_layer.show_swath(t, period=dt.total_seconds()/60.0)


    def fill_sampling(self, filepath, contiguous=True):
        """
        Given a valid filepath, returns full set of filepaths 
        that complete this satellite pass, subsets and granules
        that intersect the AOI.
        """
        # make sure filepath is validated
        if self.validate( filepath ) is False:
            raise GranuleFilterError("Fill sampling requires a validated filepath")

        # add full subset to pass
        t = self.source_file_name_parser.time_from_filename(filepath)
        full_sample = self.source_file_name_parser.filenames_from_time(t)

        # step outwards, recording granules that intersect AOI,
        dt = self.get_time_step()
        # step 1/2 an orbit in either direction to look for pass granules
        n_steps = int( self.orbital_layer.orbital_period()/(dt.total_seconds()/60)/2.0 )
        # fwd fill
        for i in range(n_steps):
            if self.check_sampling_from_time(t+i*dt):
                full_sample += self.source_file_name_parser.filenames_from_time(t+i*dt)
            elif contiguous:
                break
        # bwd fill
        for i in range(n_steps):
            if self.check_sampling_from_time(t-i*dt):
                full_sample += self.source_file_name_parser.filenames_from_time(t-i*dt)
            elif contiguous:
                break

        # return result as GranuleBiDict
        return self.translate(full_sample)
