
import unittest

from pygranule.orbital_granule_filter import OrbitalGranuleFilter


class TestOrbitalGranuleFilter(unittest.TestCase):
    def setUp(self):
        config = {'config_name':"DummySatData",
                  'sat_name':"NOAA 19",
                  'instrument':"AVHRR",
                  'file_source_pattern':"/home/msg/archive/AVHRR/avhrr_%Y%m%d_%H%M00_noaa19.hrp.bz2",
                  'time_step':"00:01:00",
                  'time_step_offset':"00:00:00",
                  'area_of_interest':"(-25,62.5),(-25,67),(-13,67),(-13,62.5)"}
                  #'area_of_interest':"(-45,60),(-45,80),(40,80),(5,60)"}
        self.af = OrbitalGranuleFilter(config)
        # override orbital_layer with a particular TLE orbital element.
        self.af.orbital_layer.set_tle("1 29499U 06044A   11254.96536486  .00000092  00000-0  62081-4 0  5221",
                                      "2 29499  98.6804 312.6735 0001758 111.9178 248.2152 14.21501774254058")

    def test_validate(self):
        # Run
        result1 = self.af.validate("/home/msg/archive/AVHRR/avhrr_20140225_133400_noaa19.hrp.bz2")
        result2 = self.af.validate("/home/msg/archive/AVHRR/avhrr_20140225_133500_noaa19.hrp.bz2")
        result3 = self.af.validate("/home/msg/archive/AVHRR/avhrr_20140225_133600_noaa19.hrp.bz2")
        result4 = self.af.validate("/home/msg/archive/AVHRR/avhrr_20140225_133700_noaa19.hrp.bz2")
        result5 = self.af.validate("/home/msg/archive/AVHRR/avhrr_20140225_160000_noaa19.hrp.bz2")
        # Assert
        self.assertTrue(result1)
        self.assertTrue(result2)
        self.assertTrue(result3)
        self.assertFalse(result4)
        self.assertFalse(result5)

    def test_filter(self):
        # Run
        files = ["blabla",
                 "H-000-MSG3__-MSG3________-WV_073___-000009___-201401231300",
                 "/home/msg/archive/AVHRR/avhrr_20140225_133400_noaa19.hrp.bz2",
                 "/home/msg/archive/AVHRR/avhrr_20140225_133500_noaa19.hrp.bz2",
                 "/home/msg/archive/AVHRR/avhrr_20140225_133600_noaa19.hrp.bz2",
                 "/home/msg/archive/AVHRR/avhrr_20140225_133700_noaa19.hrp.bz2",
                 "/home/msg/archive/AVHRR/avhrr_20140225_160000_noaa19.hrp.bz2",
                 "H-000-MSG3__-MSG3________-IR_108___-000003___-201401231300"]
        result = self.af(files)
        # Assert
        self.assertItemsEqual(result,[files[2],files[3],files[4]])

    def test_fill_pass(self):
        # Run
        result = self.af.fill_sampling("/home/msg/archive/AVHRR/avhrr_20140225_133500_noaa19.hrp.bz2")
        # Assert
        self.assertItemsEqual(result, ["/home/msg/archive/AVHRR/avhrr_20140225_133400_noaa19.hrp.bz2",
                                       "/home/msg/archive/AVHRR/avhrr_20140225_133500_noaa19.hrp.bz2",
                                       "/home/msg/archive/AVHRR/avhrr_20140225_133600_noaa19.hrp.bz2"])


