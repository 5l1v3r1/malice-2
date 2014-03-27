import os
import unittest
from nose.tools import ok_
from app.worker.av.clamav.scanner import clamav_engine
from app.worker.av.generic.test.common import AVEngineTemplate, EvilnessEngineTemplate
from lib.scanworker.file import PickleableFileSample


class TestClamAV(AVEngineTemplate, EvilnessEngineTemplate, unittest.TestCase):
    scan_class = clamav_engine
    infected_string = 'Eicar-Test-Signature'


    def setUp(self):
        AVEngineTemplate.setUp(self)

    def test_update(self):
        """
		Run test of A/V definition update functionality.

		This test requires root privs (sudo or setuid root).
		"""

        # version returns dict, test needs 'definitions' element.
        # definitions is string like: 15481
        # initial ver on A/V defs
        init_ver = self.scanner.version['definitions']
        #print init_ver

        # run update_definitions()
        self.scanner.update_definitions()
        # final date on A/V defs
        final_ver = self.scanner.version['definitions']
        #print final_ver

        # If the defs were updated, final_ver is > init_ver.
        # In the case where they were already updated, then final_ver == init_ver.
        ok_(final_ver >= init_ver, msg="Test A/V def update - version")

    def test_scan(self):
        malware = 'eicar.com.txt'
        # malware = 'blat.ex_'
        my_clamav_engine = clamav_engine()
        TEST_FILE_DIR_PATH = os.path.join(os.path.dirname(__file__), '..', 'file')
        path = PickleableFileSample.path_factory(os.path.join(TEST_FILE_DIR_PATH, malware))
        # path = os.path.join(TEST_FILE_DIR_PATH, 'eicar.com.txt')
        my_scan = my_clamav_engine.scan(path)
        if my_scan.infected:
            print
            print "Infected:"
            print my_scan.infected_string
            print
        ok_(my_scan, msg="Test A/V def update - version")

