
import unittest

from pygranule.periodic_granule_filter import PeriodicGranuleFilter
import os, shutil

def make_dummy_file(path):
    open(path, 'w').close()


class TestPeriodicGranuleFilter(unittest.TestCase):
    def setUp(self):
        config = {'config_name':"DummySatData",
                  'sat_name':"DummySat",
                  'protocol':"local",
                  'file_source_pattern':"/tmp/test_pygranule/source/{0}/H-000-MSG3__-MSG3________-{0}___-00000{1}___-%Y%m%d%H%M",
                  'subsets':"{IR_108:{1..8}}",
                  'time_step':"00:15:00",
                  'time_step_offset':"00:00:00",
                  'file_destination_pattern':"/tmp/test_pygranule/destin/{0}_{1}_%Y%m%d%H%M"}
        # set up some dummy source files and folders
        self.files = ["blabla",
                 "/tmp/test_pygranule/source/IR_108/H-000-MSG3__-MSG3________-IR_108___-000004___-201401231315",
                 "/tmp/test_pygranule/source/WV_073/H-000-MSG3__-MSG3________-WV_073___-000002___-201401231355",
                 "/tmp/test_pygranule/source/WV_073/H-000-MSG3__-MSG3________-WV_073___-000009___-201401231300",
                 "/tmp/test_pygranule/source/IR_108/H-000-MSG3__-MSG3________-{0}___-00000{1}___-%Y%m%d%H%M",
                 "/tmp/test_pygranule/source/IR_108/H-000-MSG3__-MSG3________-IR_108___-000003___-201401231300"]

        os.mkdir("/tmp/test_pygranule")
        os.mkdir("/tmp/test_pygranule/source")
        os.mkdir("/tmp/test_pygranule/source/IR_108")
        os.mkdir("/tmp/test_pygranule/source/WV_073")
        make_dummy_file("/tmp/test_pygranule/source/IR_108/bla")
        make_dummy_file("/tmp/test_pygranule/source/IR_108/H-000-MSG3__-MSG3________-IR_108___-000005___-201402202301")
        make_dummy_file("/tmp/test_pygranule/source/IR_108/H-000-MSG3__-MSG3________-IR_108___-000005___-201402202300")
        make_dummy_file("/tmp/test_pygranule/source/IR_108/H-000-MSG3__-MSG3________-IR_108___-000005___-201402200645")
        
        # create the filter
        self.af = PeriodicGranuleFilter(config)

    def tearDown(self):
        shutil.rmtree("/tmp/test_pygranule")

    def test_validate(self):
        # Run
        result1 = self.af.validate("blabla")
        result2 = self.af.validate("")
        result3 = self.af.validate("/tmp/test_pygranule/source/{0}/H-000-MSG3__-MSG3________-{0}___-00000{1}___-%Y%m%d%H%M")
        result4 = self.af.validate("/tmp/test_pygranule/source/IR_108/H-000-MSG3__-MSG3________-IR_108___-000005___-%Y%m%d%H%M")
        result5 = self.af.validate("/tmp/test_pygranule/source/IR_108/H-000-MSG3__-MSG3________-IR_108___-000005___-201402202301")
        result6 = self.af.validate("/tmp/test_pygranule/source/IR_108/H-000-MSG3__-MSG3________-IR_108___-000005___-201402202300")
        # Assert
        self.assertFalse(result1)
        self.assertFalse(result2)
        self.assertFalse(result3)
        self.assertFalse(result4)
        self.assertFalse(result5)
        self.assertTrue(result6)

    def test_filter(self):
        # Run
        result = self.af(self.files)
        # Assert
        self.assertItemsEqual(result,[self.files[1],self.files[5]])

    def test_getitem(self):
        # Run
        value = self.af['time_step']
        # Assert
        self.assertEqual(value,"00:15:00")

    def test_check_source(self):
        # Run
        result = self.af.list_source()
        # Assert
        self.assertItemsEqual( zip(result.keys(),result.values()),
                               [('/tmp/test_pygranule/source/IR_108/H-000-MSG3__-MSG3________-IR_108___-000005___-201402202300', '/tmp/test_pygranule/destin/IR_108_5_201402202300'),
                                ('/tmp/test_pygranule/source/IR_108/H-000-MSG3__-MSG3________-IR_108___-000005___-201402200645', '/tmp/test_pygranule/destin/IR_108_5_201402200645')] )
        
    def test_list_source_with_call(self):
        # Run
        result = self.af()
        # Assert
        self.assertItemsEqual( zip(result.keys(),result.values()),
                               [('/tmp/test_pygranule/source/IR_108/H-000-MSG3__-MSG3________-IR_108___-000005___-201402202300', '/tmp/test_pygranule/destin/IR_108_5_201402202300'),
                                ('/tmp/test_pygranule/source/IR_108/H-000-MSG3__-MSG3________-IR_108___-000005___-201402200645', '/tmp/test_pygranule/destin/IR_108_5_201402200645')] )

