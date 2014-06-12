#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Josh Maine'
__copyright__ = '''Copyright (C) 2013-2014 Josh "blacktop" Maine
                   This file is part of Malice - https://github.com/blacktop/malice
                   See the file 'docs/LICENSE' for copying permission.'''

# Copyright (C) 2010-2014 Cuckoo Foundation.
# This file is part of Cuckoo Sandbox - http://www.cuckoosandbox.org
# See the file 'docs/LICENSE' for copying permission.

import os
import re
import logging
import time

from lib.common.config import Config
from lib.common.constants import MALICE_ROOT
from lib.common.exceptions import MaliceCriticalError
from lib.common.exceptions import MaliceMachineError
from lib.common.exceptions import MaliceOperationalError
from lib.common.exceptions import MaliceReportError
from lib.common.exceptions import MaliceDependencyError
from lib.common.objects import Dictionary
from lib.common.utils import create_folder
from lib.core.database import Database


log = logging.getLogger(__name__)

L64_PLATFORM = 'L64'
L32_PLATFORM = 'L32'
W64_PLATFORM = 'W64'
W32_PLATFORM = 'W32'

PLATFORM_CHOICES = (
    (W32_PLATFORM, 'Windows 32'),
    (W64_PLATFORM, 'Windows 64'),
    (L32_PLATFORM, 'Linux 32'),
    (L64_PLATFORM, 'Linux 64')
)


class AntiVirus(object):
    """Base class for Malice anti-virus."""

    name = ""
    description = ""
    severity = 1
    categories = []
    families = []
    authors = []
    references = []
    alert = False
    enabled = True
    minimum = None
    maximum = None

    # Higher order will be processed later (only for non-evented signatures)
    # this can be used for having meta-signatures that check on other lower-
    # order signatures being matched
    order = 0

    evented = False
    filter_processnames = set()
    filter_apinames = set()
    filter_categories = set()

    def __init__(self, data):
        self.data = data
        self.analysis_path = ""
        self.reports_path = ""
        self.task = None
        self.options = None

    @property
    def platform(self):
        '''
        OS Platform we're running on
        '''
        return self._platform

    @property
    def requires_update_file_from_master(self):
        return getattr(self, '_requires_update_file_from_master', False)

    @property
    def engine_path(self):
        return self._engine_path

    @property
    def supported_file_types(self):
        return self._supported_file_types

    @property
    def version(self):
        """Version numbers for scanner components.

        @raise NotImplementedError: this method is abstract.
        """
        raise NotImplementedError

    def is_engine_licensed(self):
        """
        Returns boolean indicating whether the scanner has a license file installed.  This function is intended to be
        overrridden by extending classes.  As not all scanners require a license file, we default this to True.
        """
        return True

    def engine_path_exists(self):
        if self._engine_path is None: return True  # not all scanners require an engine path
        exists = self._path_exists(self._engine_path)
        log.debug("Engine path existance is: {0}.".format(exists))
        return exists

    def is_engine_path_executable(self):
        if self._engine_path is None: return True  # not all scanners require an engine path
        if os.path.isfile(self._engine_path) and os.access(self._engine_path, os.X_OK):
            log.debug("Engine path '{0}' is execuatable.".format(self._engine_path))
            return True
        log.debug("Engine path '{0}' is not execuatable.".format(self._engine_path))
        return False

    def is_installed(self):
        """
        Returns boolean indicated whether all files and settings are configured for successful usage of the engine.
        This should be overridden by subclasses and given more stringent checks.
        """
        log.debug("Checking if engine {0} is installed.".format(self._name))
        return self.engine_path_exists() and self.is_engine_path_executable() and self.is_engine_licensed()

    def update_definitions(self):
        """Update analysis tool and/or definitions.

        @raise NotImplementedError: this method is abstract.
        """
        raise NotImplementedError

    def format_output(self, output):
        """Format stdout to python dict/json.

        @raise NotImplementedError: this method is abstract.
        """
        raise NotImplementedError

    def scan(self):
        """Start scanning file.
        @raise NotImplementedError: this method is abstract.
        """
        raise NotImplementedError

    def scan(self, file_object):
        if not self.is_engine_licensed():
            raise ScannerRequiresLicenseFile
        return self.do_scan(file_object)

    def do_scan(self, file_object):
        raise NotImplementedError

    def as_result(self):
        """Properties as a dict (for results).
        @return: result dictionary.
        """
        return dict(
            name=self.name,
            description=self.description,
            severity=self.severity,
            references=self.references,
            data=self.data,
            alert=self.alert,
            families=self.families
        )


class FileAnalysis(object):
    """Base class for Malice file analysis."""

    name = ""
    description = ""
    severity = 1
    categories = []
    families = []
    authors = []
    references = []
    alert = False
    enabled = True
    minimum = None
    maximum = None

    # Higher order will be processed later (only for non-evented signatures)
    # this can be used for having meta-signatures that check on other lower-
    # order signatures being matched
    order = 0

    evented = False
    filter_processnames = set()
    filter_apinames = set()
    filter_categories = set()

    def __init__(self, data):
        self.data = data
        self.analysis_path = ""
        self.reports_path = ""
        self.task = None
        self.options = None

    def update_definitions(self):
        """Update analysis tool and/or definitions.

        @raise NotImplementedError: this method is abstract.
        """
        raise NotImplementedError

    def format_output(self, output):
        """Format stdout to python dict/json.

        @raise NotImplementedError: this method is abstract.
        """
        raise NotImplementedError

    def scan(self):
        """Start scanning file.
        @raise NotImplementedError: this method is abstract.
        """
        raise NotImplementedError

    def as_result(self):
        """Properties as a dict (for results).
        @return: result dictionary.
        """
        return dict(
            name=self.name,
            description=self.description,
            severity=self.severity,
            references=self.references,
            data=self.data,
            alert=self.alert,
            families=self.families
        )


class Intel(object):
    """Base abstract class for reporting module."""
    order = 1

    def __init__(self):
        self.analysis_path = ""
        self.reports_path = ""
        self.task = None
        self.options = None

    def set_path(self, analysis_path):
        """Set analysis folder path.
        @param analysis_path: analysis folder path.
        """
        self.analysis_path = analysis_path
        self.conf_path = os.path.join(self.analysis_path, "analysis.conf")
        self.file_path = os.path.realpath(os.path.join(self.analysis_path,
                                                       "binary"))
        self.reports_path = os.path.join(self.analysis_path, "reports")
        self.shots_path = os.path.join(self.analysis_path, "shots")
        self.pcap_path = os.path.join(self.analysis_path, "dump.pcap")

        try:
            create_folder(folder=self.reports_path)
        except MaliceOperationalError as e:
            MaliceReportError(e)

    def set_options(self, options):
        """Set report options.
        @param options: report options dict.
        """
        self.options = options

    def set_task(self, task):
        """Add task information.
        @param task: task dictionary.
        """
        self.task = task

    def run(self):
        """Start report processing.
        @raise NotImplementedError: this method is abstract.
        """
        raise NotImplementedError


class Sandbox(object):
    """Base abstract class for sandbox module."""
    order = 1
    enabled = True

    def __init__(self):
        self.analysis_path = ""
        self.logs_path = ""
        self.task = None
        self.options = None

    def set_options(self, options):
        """Set report options.
        @param options: report options dict.
        """
        self.options = options

    def set_task(self, task):
        """Add task information.
        @param task: task dictionary.
        """
        self.task = task

    def set_path(self, analysis_path):
        """Set paths.
        @param analysis_path: analysis folder path.
        """
        self.analysis_path = analysis_path
        self.log_path = os.path.join(self.analysis_path, "analysis.log")
        self.file_path = os.path.realpath(os.path.join(self.analysis_path,
                                                       "binary"))
        self.dropped_path = os.path.join(self.analysis_path, "files")
        self.logs_path = os.path.join(self.analysis_path, "logs")
        self.shots_path = os.path.join(self.analysis_path, "shots")
        self.pcap_path = os.path.join(self.analysis_path, "dump.pcap")
        self.pmemory_path = os.path.join(self.analysis_path, "memory")
        self.memory_path = os.path.join(self.analysis_path, "memory.dmp")

    def run(self):
        """Start processing.
        @raise NotImplementedError: this method is abstract.
        """
        raise NotImplementedError


