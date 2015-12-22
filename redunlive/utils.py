# -*- coding: utf-8 -*-

import re
import sys
import platform

import requests
from requests.auth import HTTPBasicAuth

from . import __version__
from . import log


def clean_name( name ):
    """ replaces non-alpha with underscores '_'
        and set the string to lower case
    """
    return re.sub( '[^0-9a-zA-Z]+', '_', name ).lower()


def pull_data( url, creds=None):
    """ reads a text file from given url
        if basic auth needed, pass args creds['user'] and creds['pwd']
    """
    headers = {
            'User-Agent': default_useragent(),
            'Accept-Encoding': 'gzip, deflate',
            'Accept': 'text/html, text/*'
            }
    au = None
    if not creds is None:
        if 'user' in creds.keys() and 'pwd' in creds.keys():
            au = HTTPBasicAuth( creds['user'], creds['pwd'] )
            headers.update( {'X-REQUESTED-AUTH': 'Basic'} )

    try:
        response = requests.get( url, headers=headers, auth=au )
    except requests.HTTPError as e:
        log.warning("data from url(%s) is unavailable. Error: %s" % ( url, e ) )
        return None
    else:
        return response.text


def default_useragent():
    """Return a string representing the default user agent."""
    _implementation = platform.python_implementation()

    if _implementation == 'CPython':
        _implementation_version = platform.python_version()
    elif _implementation == 'PyPy':
        _implementation_version = '%s.%s.%s' % (sys.pypy_version_info.major,
                                                sys.pypy_version_info.minor,
                                                sys.pypy_version_info.micro)
        if sys.pypy_version_info.releaselevel != 'final':
            _implementation_version = ''.join([_implementation_version, \
                    sys.pypy_version_info.releaselevel])
    elif _implementation == 'Jython':
        _implementation_version = platform.python_version()  # Complete Guess
    elif _implementation == 'IronPython':
        _implementation_version = platform.python_version()  # Complete Guess
    else:
        _implementation_version = 'Unknown'

    try:
        p_system = platform.system()
        p_release = platform.release()
    except IOError:
        p_system = 'Unknown'
        p_release = 'Unknown'

    return " ".join(['%s/%s' % (__name__, __version__),
                    '%s/%s' % (_implementation, _implementation_version),
                    '%s/%s' % (p_system, p_release)])


