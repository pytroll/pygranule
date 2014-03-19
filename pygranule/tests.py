
import unittest

from .file_name_parser import FileNameParser
from .pyorbital_layer import PyOrbitalLayer
from .periodic_granule_filter import PeriodicGranuleFilter
from .orbital_granule_filter import OrbitalGranuleFilter
from .local_file_access_layer import LocalFileAccessLayer
from .file_set import FileSet
from .transfer_file_set import TransferFileSet
from datetime import datetime
import os
import shutil

def make_dummy_file(path):
    open(path, 'w').close()

class TestTransferFileSet(unittest.TestCase):
    def setUp(self):
        self.sfiles = ['/tmp/pygranule/source1/file1',
                        '/tmp/pygranule/source1/file2',
                        '/tmp/pygranule/source2/file3']
        self.dfiles = ['/tmp/pygranule/destin1/file1',
                        '/tmp/pygranule/destin1/file2',
                        '/tmp/pygranule/destin1/file3']

        self.tfs = TransferFileSet(self.sfiles,self.dfiles)

    def test_paths(self):
        # Run
        paths = self.tfs.paths()
        # Assert
        self.assertItemsEqual(paths, [(self.sfiles[i],self.dfiles[i]) for i,x in enumerate(self.sfiles)])

    def test_remove(self):
        # Run
        self.tfs.remove('file3')
        paths = self.tfs.paths()
        # Assert
        self.sfiles.pop()
        self.assertItemsEqual(paths, [(self.sfiles[i],self.dfiles[i]) for i,x in enumerate(self.sfiles)])

    def test_add(self):
        # Run
        self.tfs.add('/somedir/newfile','/someotherdir/newfile')
        paths = self.tfs.paths()
        # Assert
        self.sfiles.append('/somedir/newfile')
        self.dfiles.append('/someotherdir/newfile')
        self.assertItemsEqual(paths, [(self.sfiles[i],self.dfiles[i]) for i,x in enumerate(self.sfiles)]) 

class TestFileSet(unittest.TestCase):
    def setUp(self):
        self.files = ["blabla",
                      "H-000-MSG3__-MSG3________-WV_073___-000009___-201401231300",
                      "/home/msg/archive/AVHRR/avhrr_20140225_133400_noaa19.hrp.bz2",
                      "/home/msg/archive/AVHRR/avhrr_20140225_133500_noaa19.hrp.bz2",
                      "/home/msg/archive/AVHRR/avhrr_20140225_133600_noaa19.hrp.bz2",
                      "/home/msg/archive/AVHRR/avhrr_20140225_133700_noaa19.hrp.bz2",
                      "/home/msg/archive/AVHRR/avhrr_20140225_160000_noaa19.hrp.bz2",
                      "H-000-MSG3__-MSG3________-IR_108___-000003___-201401231300"]
        self.set = FileSet(self.files)
        self.set2 = FileSet(self.files[0:5])

    def test_remove(self):
        # Run
        self.set.remove("blabla")
        self.set.remove("H-000-MSG3__-MSG3________-IR_108___-000003___-201401231300")
        self.set.remove("/home/msg/archive/AVHRR/avhrr_20140225_160000_noaa19.hrp.bz2")
        self.set.remove("/home/msg/archive/AVHRR/avhrr_20140225_133700_noaa19.hrp.bz2")

        # Assert
        result = self.set.paths()
        ref = [self.files[1], self.files[2], self.files[3], self.files[4]]
        self.assertItemsEqual(result, ref )

    def test_has_file(self):
        # Run / Assert
        self.assertTrue( self.set.has_file("H-000-MSG3__-MSG3________-IR_108___-000003___-201401231300") )
        self.assertFalse( self.set.has_file("H-000-MSG3__-MSG3________-IR_108___-000003") )
        self.assertTrue( self.set.has_file("/some/other/dir/H-000-MSG3__-MSG3________-IR_108___-000003___-201401231300") )
        self.assertTrue( self.set.has_file("/home/msg/archive/AVHRR/avhrr_20140225_133500_noaa19.hrp.bz2") )
        self.assertTrue( self.set.has_file("avhrr_20140225_133500_noaa19.hrp.bz2") )

    def test_difference(self):
        # Run
        diff_set1 = self.set.difference(self.set2)
        diff_set2 = self.set2.difference(self.set)

        # Assert
        result1 = diff_set1.paths()
        ref = self.files[5:]
        self.assertItemsEqual( result1, ref )

        result2 = diff_set2.paths()
        self.assertItemsEqual( result2, [] )

class TestLocalFileAccessLayer(unittest.TestCase):
    def setUp(self):
        # make some files and dir under /tmp
        self.workdir="/tmp/test_pygranule"

        os.mkdir(self.workdir)
        os.mkdir(self.workdir+"/testdir1")
        os.mkdir(self.workdir+"/testdir2")
        make_dummy_file(self.workdir+"/file1")
        make_dummy_file(self.workdir+"/file2")
        make_dummy_file(self.workdir+"/file3")
        make_dummy_file(self.workdir+"/testdir1/file4")
        make_dummy_file(self.workdir+"/testdir1/filetoremove")

        # instance
        self.fal = LocalFileAccessLayer()

    def tearDown(self):
        shutil.rmtree(self.workdir)

    def test_list_source_directory(self):
        files = self.fal.list_source_directory(self.workdir)
        self.assertItemsEqual(files.paths(),[self.workdir+'/file1',self.workdir+'/file2',self.workdir+'/file3'])

    def test_copy_file(self):
        self.fal.copy_file(self.workdir+"/file1",self.workdir+"/testdir2/file5")
        self.assertItemsEqual( os.listdir(self.workdir+"/testdir2"), ['file5'])

    def test_remove_source_file(self):
        self.fal.remove_source_file(self.workdir+"/testdir1/filetoremove")
        self.assertItemsEqual( os.listdir(self.workdir+"/testdir1"), ['file4'] )

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
        


class TestOrbitalGranuleFilter(unittest.TestCase):
    def setUp(self):
        config = {'config_name':"DummySatData",
                  'sat_name':"NOAA 19",
                  'file_source_pattern':"/home/msg/archive/AVHRR/avhrr_%Y%m%d_%H%M00_noaa19.hrp.bz2",
                  'time_step':"00:01:00",
                  'time_step_offset':"00:00:00",
                  'area_of_interest':"(-25,62.5),(-25,67),(-13,67),(-13,62.5)"}
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
        fileset = FileSet(files)
        result = self.af(fileset)
        # Assert
        self.assertItemsEqual(result.paths(),[files[2],files[3],files[4]])

class TestPeriodicGranuleFilter(unittest.TestCase):
    def setUp(self):
        config = {'config_name':"DummySatData",
                  'sat_name':"DummySat",
                  'protocol':"local",
                  'file_source_pattern':"/tmp/seviri/{0}/H-000-MSG3__-MSG3________-{0}___-00000{1}___-%Y%m%d%H%M",
                  'subsets':"{IR_108:{1..8}}",
                  'time_step':"00:15:00",
                  'time_step_offset':"00:00:00"}
        # set up some dummy source files and folders
        os.mkdir("/tmp/seviri")
        os.mkdir("/tmp/seviri/IR_108")
        os.mkdir("/tmp/seviri/WV_073")
        make_dummy_file("/tmp/seviri/IR_108/bla")
        make_dummy_file("/tmp/seviri/IR_108/H-000-MSG3__-MSG3________-IR_108___-000005___-201402202301")
        make_dummy_file("/tmp/seviri/IR_108/H-000-MSG3__-MSG3________-IR_108___-000005___-201402202300")
        make_dummy_file("/tmp/seviri/IR_108/H-000-MSG3__-MSG3________-IR_108___-000005___-201402200645")
        
        # create the filter
        self.af = PeriodicGranuleFilter(config)

    def tearDown(self):
        shutil.rmtree("/tmp/seviri")

    def test_validate(self):
        # Run
        result1 = self.af.validate("blabla")
        result2 = self.af.validate("")
        result3 = self.af.validate("/tmp/seviri/{0}/H-000-MSG3__-MSG3________-{0}___-00000{1}___-%Y%m%d%H%M")
        result4 = self.af.validate("/tmp/seviri/IR_108/H-000-MSG3__-MSG3________-IR_108___-000005___-%Y%m%d%H%M")
        result5 = self.af.validate("/tmp/seviri/IR_108/H-000-MSG3__-MSG3________-IR_108___-000005___-201402202301")
        result6 = self.af.validate("/tmp/seviri/IR_108/H-000-MSG3__-MSG3________-IR_108___-000005___-201402202300")
        # Assert
        self.assertFalse(result1)
        self.assertFalse(result2)
        self.assertFalse(result3)
        self.assertFalse(result4)
        self.assertFalse(result5)
        self.assertTrue(result6)

    def test_filter(self):
        # Run
        files = ["blabla",
                 "/tmp/seviri/IR_108/H-000-MSG3__-MSG3________-IR_108___-000004___-201401231315",
                 "/tmp/seviri/WV_073/H-000-MSG3__-MSG3________-WV_073___-000002___-201401231355",
                 "/tmp/seviri/WV_073/H-000-MSG3__-MSG3________-WV_073___-000009___-201401231300",
                 "/tmp/seviri/IR_108/H-000-MSG3__-MSG3________-{0}___-00000{1}___-%Y%m%d%H%M",
                 "/tmp/seviri/IR_108/H-000-MSG3__-MSG3________-IR_108___-000003___-201401231300"]
        fileset = FileSet(files)
        result = self.af(fileset)
        # Assert
        self.assertItemsEqual(result.paths(),[files[1],files[5]])

    def test_getitem(self):
        # Run
        value = self.af['time_step']
        # Assert
        self.assertEqual(value,"00:15:00")

    def test_check_source(self):
        # Run
        result = self.af.check_source()
        # Assert
        self.assertItemsEqual( result.paths(),
                               ["/tmp/seviri/IR_108/H-000-MSG3__-MSG3________-IR_108___-000005___-201402202300",
                                "/tmp/seviri/IR_108/H-000-MSG3__-MSG3________-IR_108___-000005___-201402200645"])

    def test_check_source_with_call(self):
        # Run
        result = self.af()
        # Assert
        self.assertItemsEqual( result.paths(),
                               ["/tmp/seviri/IR_108/H-000-MSG3__-MSG3________-IR_108___-000005___-201402202300",
                                "/tmp/seviri/IR_108/H-000-MSG3__-MSG3________-IR_108___-000005___-201402200645"])

class TestFileNameParser(unittest.TestCase):
    def setUp(self):
        self.fnp = FileNameParser("/seviri/{0}/H-000-MSG3__-MSG3________-{0}___-00000{1}___-%Y%m%d%H%M",
                             "{IR_108:{1..8}, WV_073:{1,2,3,4,5,6,7,8}}")

    def test_filenames_from_time(self):
        reference_filenames = ['/seviri/IR_108/H-000-MSG3__-MSG3________-IR_108___-000001___-201401231355',
                               '/seviri/IR_108/H-000-MSG3__-MSG3________-IR_108___-000003___-201401231355',
                               '/seviri/IR_108/H-000-MSG3__-MSG3________-IR_108___-000002___-201401231355',
                               '/seviri/IR_108/H-000-MSG3__-MSG3________-IR_108___-000005___-201401231355',
                               '/seviri/IR_108/H-000-MSG3__-MSG3________-IR_108___-000004___-201401231355',
                               '/seviri/IR_108/H-000-MSG3__-MSG3________-IR_108___-000007___-201401231355',
                               '/seviri/IR_108/H-000-MSG3__-MSG3________-IR_108___-000006___-201401231355',
                               '/seviri/IR_108/H-000-MSG3__-MSG3________-IR_108___-000008___-201401231355',
                               '/seviri/WV_073/H-000-MSG3__-MSG3________-WV_073___-000001___-201401231355',
                               '/seviri/WV_073/H-000-MSG3__-MSG3________-WV_073___-000003___-201401231355',
                               '/seviri/WV_073/H-000-MSG3__-MSG3________-WV_073___-000002___-201401231355',
                               '/seviri/WV_073/H-000-MSG3__-MSG3________-WV_073___-000005___-201401231355',
                               '/seviri/WV_073/H-000-MSG3__-MSG3________-WV_073___-000004___-201401231355',
                               '/seviri/WV_073/H-000-MSG3__-MSG3________-WV_073___-000007___-201401231355',
                               '/seviri/WV_073/H-000-MSG3__-MSG3________-WV_073___-000006___-201401231355',
                               '/seviri/WV_073/H-000-MSG3__-MSG3________-WV_073___-000008___-201401231355']
        # Run
        t = datetime(2014,1,23,13,55)
        filenames = self.fnp.filenames_from_time(t)
        # Assert
        self.assertItemsEqual( filenames, reference_filenames )
    
    def test_time_from_filename(self):
        reference_t = datetime(2014,1,23,13,55)
        # Run
        t = self.fnp.time_from_filename("/seviri/WV_073/H-000-MSG3__-MSG3________-WV_073___-000006___-201401231355")
        # Assert
        self.assertEqual( t, reference_t )

    def test_validate_filename(self):
        # Run
        result1 = self.fnp.validate_filename("/seviri/WV_073/H-000-MSG3__-MSG3________-WV_073___-000006___-201401231355")
        result2 = self.fnp.validate_filename("/seviri/WV_073/H-000-MSG3__-MSG3________-WV_073___-00000X___-201401231355")
        # Assert
        self.assertTrue( result1 )
        self.assertFalse( result2 )

    def test_subset_from_filename(self):
        # Run
        subs1 = self.fnp.subset_from_filename('/seviri/WV_073/H-000-MSG3__-MSG3________-WV_073___-000003___-201401231355')
        # Assert
        self.assertItemsEqual(subs1,('WV_073', '3'))
        self.assertRaises(ValueError, self.fnp.subset_from_filename, ('/seviri/WV_073/H-000-MSG3__-MSG3________-Bla___-000003___-201401231355'))

    def test_directories(self):
        # Run
        dirs = self.fnp.directories()
        # Assert
        self.assertItemsEqual(dirs, ('/seviri/WV_073','/seviri/IR_108'))
