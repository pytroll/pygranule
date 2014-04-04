
import unittest
from pygranule.ssh_file_access_layer import SSHFileAccessLayer


class TestSSHFileAccessLayer(unittest.TestCase):

    def setUp(self):
        self.password = "..."
        self.sfal = SSHFileAccessLayer("localhost","sat",self.password)

    def test_list_source_directory(self):
        files = self.sfal.list_source_directory("/tmp/")
        print files


