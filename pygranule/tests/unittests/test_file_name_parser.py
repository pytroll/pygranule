
import unittest

from pygranule.file_name_parser import FileNameParser
from datetime import datetime

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
