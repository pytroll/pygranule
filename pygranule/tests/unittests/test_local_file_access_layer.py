
import unittest
from mock import Mock

from pygranule.local_file_access_layer import LocalFileAccessLayer

def make_dummy_file(path):
    open(path, 'w').close()

class TestLocalFileAccessLayer(unittest.TestCase):
    def setUp(self):
        # instance
        self.fal = LocalFileAccessLayer()
        # mock
        self.fal.os.listdir = Mock(return_value=['file1','file2','file3'])
        self.fal.os.path.isfile = Mock(return_value=True)
        self.fal.os.path.isdir = Mock()
        self.fal.os.makedirs = Mock(return_value=True)
        self.fal.shutil.copyfile = Mock()

    def tearDown(self):
        pass

    def test_list_source_directory(self):
        files = self.fal.list_source_directory('/somedir')
        self.assertItemsEqual(files,['/somedir/file1','/somedir/file2','/somedir/file3'])

    def test_copy_file(self):
        self.assertIsNone( self.fal.copy_file("/somedir/file1","/somedir/file5") )

    #def test_remove_source_file(self):
    #    self.fal.remove_source_file(self.workdir+"/testdir1/filetoremove")
    #    self.assertItemsEqual( os.listdir(self.workdir+"/testdir1"), ['file4'] )
