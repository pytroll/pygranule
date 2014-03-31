
import unittest
from mock import Mock

from pygranule.periodic_granule_filter import PeriodicGranuleFilter
import os, shutil
from datetime import datetime

def make_dummy_file(path):
    open(path, 'w').close()


class TestPeriodicGranuleFilter(unittest.TestCase):
    def setUp(self):
        self.config = {'config_name':"DummySatData",
                  'sat_name':"DummySat",
                  'protocol':"local",
                  'file_source_pattern':"/tmp/test_pygranule/source/{0}/H-000-MSG3__-MSG3________-{0}___-00000{1}___-%Y%m%d%H%M",
                  'subsets':"{IR_108:{1..8}}",
                  'time_step':"00:15:00",
                  'time_step_offset':"00:00:00",
                  'file_destination_pattern':"/tmp/test_pygranule/destin/{0}_{1}_%Y%m%d%H%M"}

        # set up a dummy source file
        self.file = ["/tmp/test_pygranule/source/IR_108/H-000-MSG3__-MSG3________-IR_108___-000004___-201401231315"]
        
        # create the filter
        self.af = PeriodicGranuleFilter(self.config)

        # mock
        self.af.file_name_parser.validate_filename = Mock(return_value=True)
        self.af.file_name_parser.time_from_filename = Mock(return_value=datetime(2014,01,23,13,15))
        self.af.check_sampling_from_time = Mock(return_value=True)

        self.af.source_file_name_parser.directories = Mock(return_value=["/tmp/test_pygranule/source/IR_108"])
        self.af.file_access_layer.list_source_directory = Mock(
            return_value=["/tmp/test_pygranule/source/IR_108/H-000-MSG3__-MSG3________-IR_108___-000004___-201401231315"])
        

    def tearDown(self):
        pass

    def test_validate(self):
        # Run
        result = self.af.validate(self.file[0])

        # Assert
        self.assertTrue(result)

    def test_filter(self):
        # Run
        result = self.af(self.file)
        # Assert
        self.assertItemsEqual(result,self.file)

    def test_getitem(self):
        # Run
        value = self.af['time_step']
        # Assert
        self.assertEqual(value,self.config['time_step'])

    def test_check_source(self):
        # Run
        result = self.af.check_source()
        # Assert
        self.assertItemsEqual( zip(result.keys(),result.values()),
                               [('/tmp/test_pygranule/source/IR_108/H-000-MSG3__-MSG3________-IR_108___-000004___-201401231315', '/tmp/test_pygranule/destin/IR_108_4_201401231315')] )

      
                           
    def test_check_source_with_call(self):
        # Run
        result = self.af()
        # Assert
        self.assertItemsEqual( zip(result.keys(),result.values()),
                               [('/tmp/test_pygranule/source/IR_108/H-000-MSG3__-MSG3________-IR_108___-000004___-201401231315', '/tmp/test_pygranule/destin/IR_108_4_201401231315')] )
