from os import unlink
from os.path import exists
import tempfile
import envoy
from lib.common.out import print_error

__author__ = 'Josh Maine'

ignore_tags = ['Directory', 'File Name', 'File Permissions', 'File Modification Date/Time']

class Exif():
    def __init__(self, data):
        self.data = data

    def format_output(self, output):
        exif_tag = {}
        exif_results = output.split('\n')
        exif_results = filter(None, exif_results)
        for tag in exif_results:
            tag_part = tag.split(':', 1)
            if len(tag_part) == 2:
                if tag_part[0].strip() not in ignore_tags:
                    exif_tag[tag_part[0].strip()] = tag_part[1].strip().decode('utf-8')
        return exif_tag

    def scan(self):
        #: create tmp file
        handle, name = tempfile.mkstemp(suffix=".data", prefix="exif_")
        #: Write data stream to tmp file
        with open(name, "wb") as f:
            f.write(self.data)
        #: Run exiftool on tmp file
        try:
            r = envoy.run('exiftool ' + name, timeout=15)
        except AttributeError:
            print_error('ERROR: Exif Failed.')
            return 'trid', dict(error='Exiftool failed to run.')
        else:
            #: return key, stdout as a dictionary
            return 'exif', self.format_output(r.std_out)
        finally:
            #: delete tmp file
            unlink(name)
            # exists(name)