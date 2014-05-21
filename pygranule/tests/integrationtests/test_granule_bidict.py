import unittest
from pygranule.orbital_granule_filter import OrbitalGranuleFilter
from datetime import datetime, timedelta
import os, shutil

def make_dirs(path):
    try:
        os.makedirs(path)
    except OSError:
        pass

def make_dummy_file(path):
    make_dirs( os.path.dirname(path) )
    open(path, 'w').close()

class TestGranuleBiDict_completeness(unittest.TestCase):
    def setUp(self):
        config = {'config_name':"DummySatData",
                  'sat_name':"NOAA 19",
                  'instrument':"AVHRR",
                  'file_source_pattern':"/tmp/test_pygranule/sftp/avhrr_%Y%m%d_%H%M00_noaa19.{0}.hrp.bz2",
                  'subsets':"{L1,L2}",
                  'granule_duration':"00:01:00",
                  'time_step':"00:01:00",
                  'time_step_offset':"00:00:00",
                  'area_of_interest':"(0.0,73.0),(0.0,61.0),(-30.0,61.0),(-39,63.5),(-55.666,63.5),(-57.75,65),(-76,76),(-75,78),(-60,82),(0,90),(30,82),(0,82)"}
            
        self.gf = OrbitalGranuleFilter(config)
        # override orbital_layer with a particular TLE orbital element.
        self.gf.orbital_layer.set_tle("1 29499U 06044A   11254.96536486  .00000092  00000-0  62081-4 0  5221",
                                      "2 29499  98.6804 312.6735 0001758 111.9178 248.2152 14.21501774254058")
        # generate some filenames
        self.files = []
        t = datetime(2014,2,25,13,15)
        dt = timedelta(minutes=1.0)
        for i in range(20):
            self.files += self.gf.source_file_name_parser.filenames_from_time(t+i*dt)

    def test_missing(self):
        gf, files = self.gf, self.files
        # run
        missing = gf(files).missing()
        # assert
        self.assertItemsEqual( missing, [ "/tmp/test_pygranule/sftp/avhrr_20140225_133500_noaa19.L2.hrp.bz2",
                                          "/tmp/test_pygranule/sftp/avhrr_20140225_133500_noaa19.L1.hrp.bz2",
                                          "/tmp/test_pygranule/sftp/avhrr_20140225_133600_noaa19.L2.hrp.bz2",
                                          "/tmp/test_pygranule/sftp/avhrr_20140225_133600_noaa19.L1.hrp.bz2",
                                          "/tmp/test_pygranule/sftp/avhrr_20140225_133700_noaa19.L2.hrp.bz2",
                                          "/tmp/test_pygranule/sftp/avhrr_20140225_133700_noaa19.L1.hrp.bz2"] )

    def test_completeness(self):
        gf, files = self.gf, self.files
        compl = gf(files).completeness()
        self.assertEqual(compl, 2/3.0)

class TestGranuleBiDict_transfer(unittest.TestCase):
    def setUp(self):
        try:
            f = open("ssh_test_access","r")
            host = f.readline().strip()
            user = f.readline().strip()
            passwd = f.readline().strip()
        except:
            self.skipTest("no 'ssh_test_access' file defined")

        config = {'config_name':"DummySatData",
                  'sat_name':"NOAA 19",
                  'instrument':"AVHRR",
                  'protocol':"sftp",
                  'server':user+":"+passwd+"@"+host,
                  'file_source_pattern':"/tmp/test_pygranule/sftp/avhrr_%Y%m%d_%H%M00_noaa19.{0}.hrp.bz2",
                  'file_destination_pattern':"/tmp/test_pygranule/local/%Y/%j/{0}/n19_%H%M%S_%Y%j.{0}.hrp.bz2",
                  'subsets':"{L1,L2}",
                  'granule_duration':"00:01:00",
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
        for i in range(20):
            self.files += self.gf.source_file_name_parser.filenames_from_time(t+i*dt)
            
        # touch filenames
        for fn in self.files:
            make_dummy_file(fn)

    def tearDown(self):
        shutil.rmtree("/tmp/test_pygranule")
        del self.gf

    def test_sftp_file_transfer(self):
        # run
        sfiles = self.gf().transfer()
        # find what got copied to local fs
        local_files = []
        for path, dirs, files in os.walk('/tmp/test_pygranule/local/'):
            for f in files:
                local_files += [path+'/'+f]
        # assert
        self.assertItemsEqual(local_files, sfiles.values())
        

def niceprintdict(mydict):
    for x in mydict:
        print x,':',mydict[x]
