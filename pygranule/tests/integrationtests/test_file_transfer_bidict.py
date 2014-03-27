
import unittest

from pygranule.file_transfer_bidict import FileTransferBiDict
from pygranule.local_file_access_layer import LocalFileAccessLayer
import os, shutil

def make_dummy_file(path):
    open(path, 'w').close()

class TestFileTransferBiDict(unittest.TestCase):
    def setUp(self):
        # generate test files
        self.d = {}
        for i in range(10):
            a = "/tmp/test_pygranule/source/fileA"+str(i)
            b = "/tmp/test_pygranule/destin/fileB"+str(i)
            self.d[a] = b
        # mkdirs
        os.mkdir("/tmp/test_pygranule")
        os.mkdir("/tmp/test_pygranule/source")
        os.mkdir("/tmp/test_pygranule/destin")
        # mk dummy files
        # NOTE: might want to fill the files with some data
        for key in self.d:
            make_dummy_file(key)
        # instance
        self.lfal = LocalFileAccessLayer()
        self.ftbd = FileTransferBiDict(self.d.copy(),
                                       file_access_layer = self.lfal)
        
    def tearDown(self):
        shutil.rmtree("/tmp/test_pygranule")

    def test_transfer(self):
        # Run
        self.ftbd.transfer()
        # Assert
        self.assertItemsEqual( os.listdir("/tmp/test_pygranule/destin"),
                               [ os.path.basename(x) for x in self.d.values() ] )

