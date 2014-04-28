
import unittest
from mock import Mock
from pygranule.ssh_file_access_layer import SSHFileAccessLayer
from pygranule.file_name_parser import FileNameParser
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


class TestSSHFileAccessLayer(unittest.TestCase):

    def setUp(self):
        try:
            f = open("ssh_test_access","r")
            host = f.readline().strip()
            user = f.readline().strip()
            passwd = f.readline().strip()
        except:
            self.skipTest("no 'ssh_test_access' file defined")

        self.sfal = SSHFileAccessLayer(host, user, passwd)
            
        # create some granule file names
        fnp = FileNameParser("/tmp/test_pygranule/ssh/avhr_noaa19_%Y%m%d_%H%M.hrp")
        self.files = []
        dt = timedelta(minutes=1.0)
        t = datetime(2014,4,1,12,00)
        for i in range(20):
            self.files += fnp.filenames_from_time(t + i*dt)
        
        # touch filenames
        for fn in self.files:
            make_dummy_file(fn)
        
    def tearDown(self):
        shutil.rmtree("/tmp/test_pygranule")
        del self.sfal

    def test_list_source_directory(self):
        sshfiles = self.sfal.list_source_directory("/tmp/test_pygranule/ssh")
        self.assertItemsEqual(sshfiles,self.files)

    def test_check_for_source_file(self):
        status1 = self.sfal.check_for_source_file(self.files[0])
        status2 = self.sfal.check_for_source_file("/tmp/test_pygranule/ssh/non_existing_file")
        self.assertTrue(status1)
        self.assertFalse(status2)

    def test_copy_file(self):
        self.sfal.copy_file(self.files[0],"/tmp/test_pygranule/copied_over_file")
        self.assertTrue( "copied_over_file" in os.listdir("/tmp/test_pygranule") )
        
    def test_remove_source_file(self):
        self.sfal.remove_source_file(self.files[0])
        self.assertFalse( os.path.isfile(self.files[0]) )

    def test_connection_retention(self):
        # list files
        sshfiles = self.sfal.list_source_directory("/tmp/test_pygranule/ssh")
        # mock out new connection - to prevent it from being called
        self.sfal._get_new_connection = Mock(return_value=None)
        # list files again
        sshfiles2 = self.sfal.list_source_directory("/tmp/test_pygranule/ssh")
        # assert behaviour is as expected
        self.assertItemsEqual(sshfiles,sshfiles2)
