# Sheepdog
# Copyright 2013 Adam Greig
#
# Released under the MIT license. See LICENSE file for details.

import os
import socket
import tempfile
from nose.tools import assert_equal, assert_raises, assert_true

from sheepdog import storage, server, serialisation, client

def get_free_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("", 0))
    port = s.getsockname()[1]
    s.close()
    return port

const = 42
def my_function(a, b):
    return a + b + const

class TestClient:
    def setup(self):
        self.db_fd, self.dbfile = tempfile.mkstemp()

        self.port = get_free_port()
        self.password = "password"
        self.server = server.Server(self.port, self.password, self.dbfile)

        self.storage = storage.Storage(dbfile=self.dbfile)
        self.storage.initdb()

        self.func = my_function
        self.ns = {"const": const}
        self.args = [(0, 0), (3, 4)]
        self.request_id = 1
        self.job_index = 2

        self.func_bin = serialisation.serialise_function(self.func)
        self.ns_bin = serialisation.serialise_namespace(self.ns)
        self.args_bin = serialisation.serialise_args(self.args)

        self.storage.new_request(self.func_bin, self.ns_bin, self.args_bin)

        self.url = "http://localhost:{0}/".format(self.port)
        self.client = client.Client(self.url, self.password,
                                    self.request_id, self.job_index)

    def teardown(self):
        self.server.stop()
        os.close(self.db_fd)
        os.unlink(self.dbfile)

    def test_gets_details(self):
        self.client.get_details()
        assert_equal(self.client.args, self.args[1])
        assert_equal(type(self.client.func), type(self.func))
        del self.client.ns["__builtins__"]
        assert_equal(self.client.ns, self.ns)

    def test_get_details_exceeds_retries(self):
        self.client.HTTP_RETRIES = 1
        self.client.url = "http://localhost:1/"
        class FakeTime:
            def sleep(self, x):
                return
        client.time = FakeTime()
        assert_raises(RuntimeError, self.client.get_details)

    def test_doesnt_run_without_details(self):
        assert_raises(RuntimeError, self.client.run)

    def test_runs_function(self):
        self.client.get_details()
        self.client.run()
        assert_true(hasattr(self.client, 'result'))
        assert_equal(self.client.result, self.func(*self.args[1]))

    def test_doesnt_submit_without_running(self):
        class FakeTime:
            def sleep(self, x):
                return
        client.time = FakeTime()
        assert_raises(RuntimeError, self.client.submit_results)
        self.client.get_details()
        assert_raises(RuntimeError, self.client.submit_results)

    def test_submits_results(self):
        self.client.get_details()
        self.client.run()
        self.client.submit_results()
        expected = serialisation.serialise_pickle(self.func(*self.args[1]))
        assert_equal(self.storage.get_results(self.request_id),
            [(self.args_bin[1], expected)])

    def test_submit_exceeds_retries(self):
        self.client.get_details()
        self.client.run()
        self.client.HTTP_RETRIES = 1
        self.client.url = "http://localhost:1/"
        class FakeTime:
            def sleep(self, x):
                return
        client.time = FakeTime()
        assert_raises(RuntimeError, self.client.submit_results)

    def test_submits_errors(self):
        self.client.get_details()
        self.client.run()
        self.client._submit_error("oops")
        assert_equal(self.storage.get_errors(self.request_id),
            [(self.args_bin[1], "oops")])

    def test_go_wrapper(self):
        self.client.go()
        expected = serialisation.serialise_pickle(self.func(*self.args[1]))
        assert_equal(self.storage.get_results(self.request_id),
            [(self.args_bin[1], expected)])

    def test_catches_exceptions(self):
        def bad_function(a, b):
            def inner(x):
                class MyOwnException(ValueError):
                    pass
                raise MyOwnException("oopsie!")
            inner(0)
        func_bin = serialisation.serialise_function(bad_function)
        request_id = self.storage.new_request(func_bin, self.ns_bin,
                                              self.args_bin)
        client.Client(self.url, self.password, request_id, self.job_index).go()

        assert_true("MyOwnException: oopsie!" in
                    self.storage.get_errors(request_id)[0][1])
