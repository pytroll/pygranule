
import unittest

from pygranule.pyorbital_layer import PyOrbitalLayer
from datetime import datetime

class TestPyOrbitalLayer(unittest.TestCase):
    def setUp(self):
        self.ol = PyOrbitalLayer( ((-25,62.5),(-25,67),(-13,67),(-13,62.5)),
                                  "NOAA 19",
                                  "AVHRR" )
        # override orbital_layer with a particular TLE orbital element.
        self.ol.set_tle("1 29499U 06044A   11254.96536486  .00000092  00000-0  62081-4 0  5221",
                        "2 29499  98.6804 312.6735 0001758 111.9178 248.2152 14.21501774254058")
        
    def test_next_transit(self):
        start_t = datetime(2014,1,23,13,01)
        t = self.ol.next_transit(start_t)
        t_ref = datetime(2014,1,23,13,26,7)
        
        dt = t - t_ref

        self.assertTrue( abs(dt.total_seconds()) < 1.0 )
        

