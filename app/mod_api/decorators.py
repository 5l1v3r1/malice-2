#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Josh Maine'

import functools
import hashlib
import time
from functools import update_wrapper

from flask import current_app, g, jsonify, make_response, request, url_for

from redis import Redis

from .errors import not_modified, precondition_failed, too_many_requests

# from app.mod_api.rate_limit import RateLimit

redis = Redis()


class RateLimit(object):
    expiration_window = 10

    def __init__(self, key_prefix, limit, per, send_x_headers):
        self.reset = (int(time.time()) // per) * per + per
        self.key = key_prefix + str(self.reset)
        self.limit = limit
        self.per = per
        self.send_x_headers = send_x_headers
        p = redis.pipeline()
        p.incr(self.key)
        p.expireat(self.key, self.reset + self.expiration_window)
        self.current = min(p.execute()[0], limit)

    remaining = property(lambda x: x.limit - x.current)
    over_limit = property(lambda x: x.current >= x.limit)


def get_view_rate_limit():
    return getattr(g, '_view_rate_limit', None)


def on_over_limit(limit):
    return 'You hit the rate limit', 400


def ratelimit(limit, per=300, send_x_headers=True,
              over_limit=on_over_limit,
              scope_func=lambda: request.remote_addr,
              key_func=lambda: request.endpoint):
    def decorator(f):
        def rate_limited(*args, **kwargs):
            key = 'rate-limit/%s/%s/' % (key_func(), scope_func())
            rlimit = RateLimit(key, limit, per, send_x_headers)
            g._view_rate_limit = rlimit
            if over_limit is not None and rlimit.over_limit:
                return over_limit(rlimit)
            return f(*args, **kwargs)

        return update_wrapper(rate_limited, f)

    return decorator

def json(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        rv = f(*args, **kwargs)
        status_or_headers = None
        headers = None
        if isinstance(rv, tuple):
            rv, status_or_headers, headers = rv + (None,) * (3 - len(rv))
        if isinstance(status_or_headers, (dict, list)):
            headers, status_or_headers = status_or_headers, None
        if not isinstance(rv, dict):
            rv = rv.to_json()
        rv = jsonify(rv)
        if status_or_headers is not None:
            rv.status_code = status_or_headers
        if headers is not None:
            rv.headers.extend(headers)
        return rv
    return wrapped


def rate_limit(limit, per, scope_func=lambda: request.remote_addr):
    def decorator(f):
        @functools.wraps(f)
        def wrapped(*args, **kwargs):
            if current_app.config['USE_RATE_LIMITS']:
                key = 'rate-limit/%s/%s/' % (f.__name__, scope_func())
                limiter = RateLimit(key, limit, per)
                if not limiter.over_limit:
                    rv = f(*args, **kwargs)
                else:
                    rv = too_many_requests('You have exceeded your request rate')
                # rv = make_response(rv)
                g.headers = {
                    'X-RateLimit-Remaining': str(limiter.remaining),
                    'X-RateLimit-Limit': str(limiter.limit),
                    'X-RateLimit-Reset': str(limiter.reset)
                }
                return rv
            else:
                return f(*args, **kwargs)
        return wrapped
    return decorator


def paginate(max_per_page=10):
    def decorator(f):
        @functools.wraps(f)
        def wrapped(*args, **kwargs):
            page = request.args.get('page', 1, type=int)
            per_page = min(request.args.get('per_page', max_per_page,
                                            type=int), max_per_page)
            query = f(*args, **kwargs)
            p = query.paginate(page, per_page)
            pages = {'page': page, 'per_page': per_page,
                     'total': p.total, 'pages': p.pages}
            if p.has_prev:
                pages['prev'] = url_for(request.endpoint, page=p.prev_num,
                                        per_page=per_page,
                                        _external=True, **kwargs)
            else:
                pages['prev'] = None
            if p.has_next:
                pages['next'] = url_for(request.endpoint, page=p.next_num,
                                        per_page=per_page,
                                        _external=True, **kwargs)
            else:
                pages['next'] = None
            pages['first'] = url_for(request.endpoint, page=1,
                                     per_page=per_page, _external=True,
                                     **kwargs)
            pages['last'] = url_for(request.endpoint, page=p.pages,
                                    per_page=per_page, _external=True,
                                    **kwargs)
            return jsonify({
                'urls': [item.get_url() for item in p.items],
                'meta': pages
            })
        return wrapped
    return decorator


def cache_control(*directives):
    def decorator(f):
        @functools.wraps(f)
        def wrapped(*args, **kwargs):
            rv = f(*args, **kwargs)
            rv = make_response(rv)
            rv.headers['Cache-Control'] =', '.join(directives)
            return rv
        return wrapped
    return decorator


def no_cache(f):
    return cache_control('no-cache', 'no-store', 'max-age=0')(f)


def etag(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        # only for HEAD and GET requests
        assert request.method in ['HEAD', 'GET'],\
            '@etag is only supported for GET requests'
        rv = f(*args, **kwargs)
        rv = make_response(rv)
        etag = '"' + hashlib.md5(rv.get_data()).hexdigest() + '"'
        rv.headers['ETag'] = etag
        if_match = request.headers.get('If-Match')
        if_none_match = request.headers.get('If-None-Match')
        if if_match:
            etag_list = [tag.strip() for tag in if_match.split(',')]
            if etag not in etag_list and '*' not in etag_list:
                rv = precondition_failed()
        elif if_none_match:
            etag_list = [tag.strip() for tag in if_none_match.split(',')]
            if etag in etag_list or '*' in etag_list:
                rv = not_modified()
        return rv
    return wrapped
