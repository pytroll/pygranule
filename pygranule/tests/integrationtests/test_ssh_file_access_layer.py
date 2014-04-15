
import unittest
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
            self.sfal = SSHFileAccessLayer(host, user, passwd)
        except:
            self.skipTest("no 'ssh_test_access' file defined")
            
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

    def test_list_source_directory(self):
        sshfiles = self.sfal.list_source_directory("/tmp/test_pygranule/ssh")
        self.assertItemsEqual(sshfiles,self.files)




