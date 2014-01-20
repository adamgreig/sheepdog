# Sheepdog
# Copyright 2013 Adam Greig
#
# Released under the MIT license. See LICENSE file for details.

import os
import json
import time
import socket
import requests
import tempfile
from nose.tools import assert_equals

from sheepdog import server, storage, serialisation


def get_free_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("", 0))
    port = s.getsockname()[1]
    s.close()
    return port

class TestServer:
    def setup(self):
        self.db_fd, self.dbfile = tempfile.mkstemp()
        self.storage = storage.Storage(dbfile=self.dbfile)
        self.storage.initdb()
        self.storage.new_request(b"myfunc", b"ns", [b"a", b"b", b"c"])
        server.app.config['TESTING'] = True
        server.app.config['DBFILE'] = self.dbfile
        self.port = get_free_port()
        self.server = server.Server(port=self.port, dbfile=self.dbfile)
        self.app = server.app.test_client()

    def teardown(self):
        self.server.stop()
        os.close(self.db_fd)
        os.unlink(self.dbfile)

    def test_gets_config(self):
        response = self.app.get('/?request_id=1&job_index=2')
        response = json.loads(response.data.decode())
        assert response['func'] == "myfunc"
        assert response['args'] == "b"

    def test_submits_result(self):
        result = b"abc"
        response = self.app.post(
            '/', data=dict(request_id=1, job_index=2, result=result))
        assert response.data == b"OK"
        assert self.storage.get_results(1) == [(b"b", b"abc")]

    def test_submits_error(self):
        error = "oops"
        response = self.app.post(
            '/error', data=dict(request_id=1, job_index=2, error=error))
        assert response.data == b"OK"
        assert self.storage.get_errors(1) == [(b"b", error)]

    def test_runs_server(self):
        # note that the server actually takes a short while to start up, so
        # requests might error out the first few times.
        port = self.port
        url = "http://localhost:{0}/?request_id=1&job_index=2".format(port)
        tries = 0
        while tries < 30:
            try:
                r = requests.get(url).json()
                break
            except requests.ConnectionError:
                tries += 1
                continue
        if tries == 30:
            raise RuntimeError("Could not connect to server after 30 tries.")
        assert r['args'] == "b"
