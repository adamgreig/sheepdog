# Sheepdog
# Copyright 2013 Adam Greig
#
# Released under the MIT license. See LICENSE file for details.

import os
import json
import time
import base64
import tempfile
from nose.tools import assert_equals

# The lengths I'll go to to avoid having any dependencies in the client code.
try:
    from urllib.error import URLError
    from urllib.parse import urlencode
    from urllib.request import urlopen, Request
except ImportError:
    from urllib import urlencode
    from urllib2 import urlopen, Request, URLError

from sheepdog import server, storage, serialisation


class TestServer:
    def setup(self):
        self.db_fd, self.dbfile = tempfile.mkstemp()
        self.storage = storage.Storage(dbfile=self.dbfile)
        self.storage.initdb()
        self.storage.new_request(b"myfunc", b"ns", [b"a", b"b", b"c"])
        self.password = "password"
        server.app.config['TESTING'] = True
        server.app.config['DBFILE'] = self.dbfile
        server.app.config['PASSWORD'] = self.password
        self.port = server._get_free_port()
        self.server = server.Server(self.port, self.password, self.dbfile)
        self.app = server.app.test_client()

    def teardown(self):
        del self.server
        os.close(self.db_fd)
        os.unlink(self.dbfile)

    def authenticated_request(self, method, url, data=None):
        authstr = base64.b64encode(("sheepdog:" + self.password).encode())
        authhdr = {"Authorization": "Basic " + authstr.decode()}
        return self.app.open(url, method=method, data=data, headers=authhdr)

    def get(self, url):
        return self.authenticated_request('GET', url)

    def post(self, url, data):
        return self.authenticated_request('POST', url, data)

    def test_gets_config(self):
        response = self.get('/?request_id=1&job_index=2')
        response = json.loads(response.data.decode())
        assert response['func'] == "myfunc"
        assert response['args'] == "b"

    def test_submits_result(self):
        result = b"abc"
        response = self.post(
            '/', data=dict(request_id=1, job_index=2, result=result))
        assert response.data == b"OK"
        assert self.storage.get_results(1) == [(b"b", b"abc")]

    def test_submits_error(self):
        error = "oops"
        response = self.post(
            '/error', data=dict(request_id=1, job_index=2, error=error))
        assert response.data == b"OK"
        assert self.storage.get_errors(1) == [(b"b", error)]

    def test_requires_password(self):
        response = self.app.get('/?request_id=1&job_index=2')
        assert response.status_code == 401

    def test_requires_correct_password(self):
        authstr = base64.b64encode(("sheepdog:" + "wrong").encode())
        authhdr = {"Authorization": "Basic " + authstr.decode()}
        response = self.app.open('/?request_id=1&job_index=2', method='GET',
                                 headers=authhdr)
        assert response.status_code == 401


    def test_runs_server(self):
        # note that the server actually takes a short while to start up, so
        # requests might error out the first few times.
        port = self.port
        url = "http://localhost:{0}/?request_id=1&job_index=2".format(port)
        userpass = ("sheepdog:" + self.password).encode()
        authstr = "Basic " + base64.b64encode(userpass).decode()
        req = Request(url, headers={"Authorization": authstr})
        tries = 0
        while tries < 30:
            try:
                response = urlopen(req)
                break
            except URLError:
                tries += 1
                continue
        if tries == 30:
            raise RuntimeError("Could not connect to server after 30 tries.")
        result = json.loads(response.read().decode())
        assert result['args'] == "b"

    def test_runs_on_some_port(self):
        del self.server
        self.server = server.Server(None, self.password, self.dbfile)
        self.port = self.server.port
        assert self.port
        self.test_runs_server()

    def test_server_requires_password(self):
        port = self.port
        url = "http://localhost:{0}/?request_id=1&job_index=2".format(port)
        tries = 0
        while tries < 30:
            try:
                response = urlopen(url)
                break
            except URLError as e:
                if hasattr(e, 'code') and e.code == 401:
                    return
                else:
                    tries += 1
                    continue
        if tries == 30:
            raise RuntimeError("Could not connect to server after 30 tries.")

    def test_server_requires_correct_password(self):
        port = self.port
        url = "http://localhost:{0}/?request_id=1&job_index=2".format(port)
        userpass = ("sheepdog:" + "wrong").encode()
        authstr = "Basic " + base64.b64encode(userpass).decode()
        req = Request(url, headers={"Authorization": authstr})
        tries = 0
        while tries < 30:
            try:
                response = urlopen(req)
                break
            except URLError as e:
                if hasattr(e, 'code') and e.code == 401:
                    return
                else:
                    tries += 1
                    continue
        if tries == 30:
            raise RuntimeError("Could not connect to server after 30 tries.")
