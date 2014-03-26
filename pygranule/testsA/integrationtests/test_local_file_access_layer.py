
import unittest

from pygranule.local_file_access_layer import LocalFileAccessLayer
import os, shutil

def make_dummy_file(path):
    open(path, 'w').close()

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
        self.assertItemsEqual(files,[self.workdir+'/file1',self.workdir+'/file2',self.workdir+'/file3'])

    def test_copy_file(self):
        self.fal.copy_file(self.workdir+"/file1",self.workdir+"/testdir2/file5")
        self.assertItemsEqual( os.listdir(self.workdir+"/testdir2"), ['file5'])

    def test_remove_source_file(self):
        self.fal.remove_source_file(self.workdir+"/testdir1/filetoremove")
        self.assertItemsEqual( os.listdir(self.workdir+"/testdir1"), ['file4'] )
