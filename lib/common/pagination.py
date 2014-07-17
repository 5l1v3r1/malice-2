#!/usr/bin/env python
# -*- coding: utf-8 -*-
from math import ceil

__author__ = 'Josh Maine'
__copyright__ = 'http://blog.jmoz.co.uk/jquery-infinite-scroll-flask-bootstrap/'


class Pagination(object):
    """A Pagination object to be used for querying and displaying pagination
    links on frontend

    Example usage:

    >>> p = Pagination(total=15, per_page=5, current_page=1)
    >>> p.start
    0
    >>> p.pages
    [1, 2, 3]
    >>> p.next_page
    2
    >>> p.current_page = 2
    >>> p.prev_page
    1
    >>> p.next_page
    3
    >>> p.start
    5

    :copyright: (c) 2013 James Morris http://jmoz.co.uk.
    """

    def __init__(self, total=None, per_page=100, current_page=1):
        """init with total number of items in your set, how many you want
        per_page, and set the current_page you are on
        """
        self.total = total
        self.per_page = per_page
        self.current_page = current_page

    def __repr__(self):
        return str(self.__dict__)

    @property
    def total_pages(self):
        """The number of pages this pagination can have due to the total and
        per_page, e.g. total 10, per_page 5 = 2 total_pages
        Cast to float so result is float, round up, then back to int
        """
        return int(ceil(float(self.total) / self.per_page))

    @property
    def pages(self):
        """Returns list of integers of pages e.g. for 3 pages [1,2,3]"""
        return range(1, self.total_pages + 1)

    @property
    def next_page(self):
        """The page number after the current_page or None"""
        return self._get_page_offset(+1)

    @property
    def prev_page(self):
        """The page number before the current_page or None"""
        return self._get_page_offset(-1)

    def _get_page_offset(self, offset):
        """Give an offset, +1 or -1 and the page number around the current_page
        will be returned So if we are on current_page 2 and pass +1 we get 3,
        if we pass -1 we get 1.  Or None if not valid
        """
        try:
            return self.pages[self.pages.index(self.current_page + offset)]
        except ValueError:
            return None

    @property
    def start(self):
        """The starting offset used when querying"""
        return self.current_page * self.per_page - self.per_page
