# !/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Josh Maine'
__copyright__ = 'https://github.com/cuckoobox/cuckoo/blob/master/lib/cuckoo/common/exceptions.py'


class MaliceCriticalError(Exception):
    """Malice struggle in a critical error."""
    pass


class MaliceStartupError(MaliceCriticalError):
    """Error starting up Malice."""
    pass


class MaliceDatabaseError(MaliceCriticalError):
    """Malice database error."""
    pass


class MaliceDependencyError(MaliceCriticalError):
    """Missing dependency error."""
    pass


class MaliceOperationalError(Exception):
    """Malice operation error."""
    pass


class MaliceAnalysisError(MaliceOperationalError):
    """Error during analysis."""
    pass


class MaliceProcessingError(MaliceOperationalError):
    """Error in processor module."""
    pass


class MaliceReportError(MaliceOperationalError):
    """Error in reporting module."""
    pass


class MaliceResultError(MaliceOperationalError):
    """Malice result server error."""
    pass