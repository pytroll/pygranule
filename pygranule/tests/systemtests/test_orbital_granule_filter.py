
from pygranule import OrbitalGranuleFilter
import unittest

from datetime import datetime, timedelta


class TestOrbitalGranuleFilter(unittest.TestCase):
    def setUp(self):
        # instantiate 
        config = {'config_name':"DummySatData",
                  'sat_name':"NOAA 19",
                  'file_source_pattern':"/home/msg/archive/AVHRR/avhrr_%Y%m%d_%H%M00_noaa19.hrp.bz2",
                  'time_step':"00:01:00",
                  'time_step_offset':"00:00:00",
                  'area_of_interest':"(0.0,73.0),(0.0,61.0),(-30.0,61.0),(-39,63.5),(-55.666,63.5),(-57.75,65),(-76,76),(-75,78),(-60,82),(0,90),(30,82),(0,82)"}
        self.gf = OrbitalGranuleFilter(config)
        # override orbital_layer with a particular TLE orbital element.
        self.gf.orbital_layer.set_tle("1 29499U 06044A   11254.96536486  .00000092  00000-0  62081-4 0  5221",
                                      "2 29499  98.6804 312.6735 0001758 111.9178 248.2152 14.21501774254058")
        # generate some filenames
        self.files = []
        t = datetime(2014,2,25,13,30)
        dt = timedelta(minutes=1.0)
        for i in range(120):
            self.files += self.gf.source_file_name_parser.filenames_from_time(t+i*dt)

    def test_show_granules(self):
        """
        Plot and display granules found in input file list.
        """
        gf = self.gf
        files = self.files

        # show all the granules
        gf.show( files )

        # show only filtered granules
        gf( files ).show()
        

