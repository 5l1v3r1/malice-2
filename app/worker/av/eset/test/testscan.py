import os
import unittest
from app.worker.av.eset.scanner import eset_engine
from app.worker.av.generic.test.common import AVEngineTemplate
from nose.tools import ok_
from lib.scanworker.file import PickleableFileSample


class TestESETAV(AVEngineTemplate, unittest.TestCase):
    scan_class = eset_engine
    infected_string = 'Eicar test file'

    def setUp(self):
        AVEngineTemplate.setUp(self)

    def test_update(self):
        """
        Run test of A/V definition update functionality.

        This test requires root privs (sudo).
        """

        # version returns dict, test needs 'definitions' element.
        # definitions is string like: 15481
        # initial ver on A/V defs
        init_ver = self.scanner.version['definitions'].split()[0]
        #print init_ver

        # run update_definitions()
        self.scanner.update_definitions()
        # final date on A/V defs
        final_ver = self.scanner.version['definitions'].split()[0]
        #print final_ver

        # If the defs were updated, final_ver is > init_ver.
        # In the case where they were already updated, then final_ver == init_ver.
        ok_(final_ver >= init_ver, msg="Test A/V def update - version")

    def test_scan(self):
        malware = 'eicar.com.txt'
        # malware = 'blat.ex_'
        my_ceset_engine = eset_engine()
        TEST_FILE_DIR_PATH = os.path.join(os.path.dirname(__file__), '..', 'file')
        path = PickleableFileSample.path_factory(os.path.join(TEST_FILE_DIR_PATH, malware))
        # path = os.path.join(TEST_FILE_DIR_PATH, 'eicar.com.txt')
        my_scan = my_ceset_engine.scan(path)
        if my_scan.infected:
            print
            print "Infected:"
            print my_scan.infected_string
            print
        ok_(my_scan, msg="Test A/V def update - version")