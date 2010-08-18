### !/usr/bin/env python
# encoding: utf-8

"""
GistAPI.py -- A Python wrapper for the Gist API
(c) 2010 Kenneth Reitz. MIT License.

Example usage:

>>> Gist('d4507e882a07ac6f9f92').repo
'd4507e882a07ac6f9f92'

>>> Gist('d4507e882a07ac6f9f92').owner
'kennethreitz'

>>> Gist('d4507e882a07ac6f9f92').description
'Example Gist for gist.py'

>>> Gist('d4507e882a07ac6f9f92').created_at
'2010/05/16 10:51:15 -0700'

>>> Gist('d4507e882a07ac6f9f92').public
False

>>> Gist('d4507e882a07ac6f9f92').filenames
['exampleEmptyFile', 'exampleFile']

>>> Gist('d4507e882a07ac6f9f92').files
{'exampleFile': 'Example file content.', uexampleEmptyFile': ''}

>>> Gists.fetch_by_user('kennethreitz')[-1].description
'My .bashrc configuration'
"""

import urllib

try:
    import simplejson as json
except ImportError:
    import json

__all__ = ['Gist', 'Gists']

GIST_BASE = 'http://gist.github.com/%s'
GIST_JSON = GIST_BASE % 'api/v1/json/%s'


class Gist(object):
    """Gist Object"""

    def __init__(self, id=None, json=None):
        self.id = id
        self._json = json

        # Map given repo id to gist id if none exists
        if self._json:
            self.id = json['repo']

        self.url = url = GIST_BASE % self.id
        self.embed_url = url + '.js'
        self.json_url = url + '.json'

    def __getattribute__(self, name):
        """Gets attributes, but only if needed"""

        # Only make external API calls if needed
        if name in ('owner', 'description', 'created_at', 'public',
                    'files', 'filenames', 'repo'):
            if not hasattr(self, '_meta'):
                self._meta = self._get_meta()

        return object.__getattribute__(self, name)

    def _get_meta(self):
        """Fetches Gist metadata"""

        # Use json data provided if available
        if self._json:
            _meta = self._json
            setattr(self, 'id', _meta['repo'])
        else:
            # Fetch Gist metadata
            _meta_url = GIST_JSON % self.id
            _meta = json.load(urllib2.urlopen(_meta_url))['gists'][0]

        for key, value in _meta.iteritems():

            if key == 'files':
                # Remap file key from API
                setattr(self, 'filenames', value)
            else:
                # Attach properties to object
                setattr(self, key, value)

        return _meta

    @property
    def files(self):
        """Fetches a gists files and stores them in the 'files' property"""
        _files = {}

        for fn in self.filenames:
            # Grab file contents
            _file_url = GIST_BASE % 'raw/%s/%s' % (self.id, fn)
            _files[fn] = urllib2.urlopen(_file_url).read()

        return _files


class Gists(object):
    """Gist API wrapper"""

    def __init__(self, username=None, token=None):
        # Token-based Authentication is unnecesary, gist api still in alpha
        self._username = username
        self._token = token

    @staticmethod
    def fetch_by_user(name):
        """Returns a list of public Gist objects owned by
        the given GitHub username"""

        _url = GIST_JSON % 'gists/%s' % name

        # Return a list of Gist objects
        return [Gist(json=g) for g in json.load(urllib.urlopen(_url))['gists']]


if __name__ == '__main__':
    import doctest
    print('hello')
    a = 'bob'

    doctest.testmod()
