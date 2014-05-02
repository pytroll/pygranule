

from .granule_filter import GranuleFilter, GranuleFilterError
from .pyorbital_layer import PyOrbitalLayer
from datetime import timedelta

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

    def split(self, filepaths):
        """
        Separates a list of input file paths into 
        chunks. File paths must have a valid file name pattern.
        Return result as list of GranuleBiDicts.
        Note: Opeartion does not pre-perform filtering.
        """
        # make datetime filepath list
        t_fp_pairs = []
        for fp in filepaths:
            # get time signature
            t = self.source_file_name_parser.time_from_filename(fp)
            t_fp_pairs.append((t,fp))
        t_fp_pairs.sort()
        # break up
        dt = timedelta(minutes=self.orbital_layer.orbital_period()/4.0)
        parts = []
        while len(t_fp_pairs) > 0:
            new_part = []
            t0 = t_fp_pairs[0][0]
            mint = t0 - dt
            maxt = t0 + dt
            while True:
                if len(t_fp_pairs) == 0:
                    parts.append(new_part)
                    break
                else:
                    t = t_fp_pairs[0][0]
       
                if (t > mint) and (t < maxt):
                    new_part.append(t_fp_pairs.pop(0)[1])                    
                else:
                    parts.append(new_part)
                    break
        # insert into list of bidicts,
        bidicts = []
        for part in parts:
            bidicts.append( self.translate(part) )

        # returned GranuleBiDict
        return bidicts

    def complete(self, filepath, contiguous=True):
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
