from os import unlink
from os.path import exists
import tempfile
import envoy
from lib.common.out import print_error

__author__ = 'Josh Maine'


class TrID():
    def __init__(self, data):
        self.data = data

    def format_output(self, output):
        trid_results = []
        results = output.split('\n')
        results = filter(None, results)
        for trid in results:
            trid_results.append(trid)
        return trid_results

    def update_definitions(self):
        #: Update the TRiD definitions
        r = envoy.run('python /opt/trid/tridupdate.py', timeout=20)

    def scan(self):
        #: create tmp file
        handle, name = tempfile.mkstemp(suffix=".data", prefix="trid_")
        #: Write data stream to tmp file
        with open(name, "wb") as f:
            f.write(self.data)
        #: Run exiftool on tmp file
        try:
            r = envoy.run('/opt/trid/trid ' + name, timeout=15)
        except AttributeError:
            print_error('ERROR: TrID Failed.')
            return 'trid', dict(error='TrID failed to run.')
        else:
            #: return key, stdout as a dictionary
            return 'trid', self.format_output(r.std_out.split(name)[-1])
        finally:
            #: delete tmp file
            unlink(name)
            # exists(name)