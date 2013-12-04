"""
Sheepdog
Copyright 2013 Adam Greig

Released under the MIT license. See LICENSE file for details.

Storage tests.
"""

import sqlite3
from nose.tools import assert_equals

from sheepdog.dog import storage

class TestStorage:
    def setup(self):
        self.storage = storage.Storage(dbfile=":memory:")
        self.storage.initdb()
        self.db = self.storage.conn
        self.c = self.db.cursor()

    def teardown(self):
        self.c.close()

    def test_creates_tables(self):
        self.c.execute("SELECT name FROM sqlite_master WHERE type='table'")
        names = self.c.fetchall()
        assert ("requests",) in names
        assert ("results",) in names
        assert ("tasks",) in names

    def add_request(self):
        f = b"i'm a function!"
        args = [b"abc", b"def", b"geh"]
        reqid = self.storage.new_request(f, args)

        return f, args, reqid

    def test_adds_request(self):
        f, args, reqid = self.add_request()

        self.c.execute("SELECT * FROM requests")
        request = self.c.fetchone()
        assert_equals(request[1], sqlite3.Binary(f))
        assert_equals(reqid, request[0])

        self.c.execute("SELECT request_id, job_index, args FROM tasks")
        tasks = self.c.fetchall()
        assert_equals(len(tasks), 3)
        assert_equals(tasks[0], (request[0], 1, sqlite3.Binary(args[0])))
        assert_equals(tasks[1], (request[0], 2, sqlite3.Binary(args[1])))
        assert_equals(tasks[2], (request[0], 3, sqlite3.Binary(args[2])))

    def test_gets_details(self):
        f, args, reqid = self.add_request()
        
        details = self.storage.get_details(reqid, 2)
        assert_equals(details, (f, args[1]))

    def store_results(self, request_id):
        results = [b"ABC", b"DEF", b"GEH"]
        for idx, result in enumerate(results):
            self.storage.store_result(request_id, idx+1, result)
        return results

    def store_results_and_errors(self, request_id):
        results = [b"ABC", b"DEF"]
        errors = ["oops"]
        for idx, result in enumerate(results):
            self.storage.store_result(request_id, idx+1, result)
        for eidx, error in enumerate(errors):
            print("storing error {0} at {1}".format(error, idx+eidx+2))
            self.storage.store_error(request_id, idx+eidx+2, error)
        return results, errors

    def test_stores_results(self):
        f, args, request_id = self.add_request()
        results = self.store_results(request_id)

        r = self.c.execute("SELECT task_id, result FROM results").fetchall()
        assert_equals(r[0][1], sqlite3.Binary(results[0]))
        assert_equals(r[1][1], sqlite3.Binary(results[1]))
        assert_equals(r[2][1], sqlite3.Binary(results[2]))

        self.c.execute("SELECT request_id, job_index FROM tasks"
                       " WHERE id=?", (r[1][0],))
        r = self.c.fetchone()
        assert_equals(r[1], 2)

    def test_gets_results(self):
        f, args, request_id = self.add_request()
        results = self.store_results(request_id)
        
        r = self.storage.get_results(request_id)

        assert_equals(r, list(zip(args, results)))

    def test_stores_errors(self):
        f, args, request_id = self.add_request()
        results, errors = self.store_results_and_errors(request_id)
        r = self.c.execute("SELECT task_id, error FROM errors").fetchall()
        assert_equals(r[0][1], errors[0])

    def test_gets_errors(self):
        f, args, request_id = self.add_request()
        results, errors = self.store_results_and_errors(request_id)
        r = self.storage.get_errors(request_id)
        assert_equals(r, list(zip(args[-1:], errors)))

    def test_counts_results(self):
        f, args, request_id = self.add_request()
        results = self.store_results(request_id)

        assert_equals(self.storage.count_results(request_id), len(results))

    def test_counts_errors(self):
        f, args, request_id = self.add_request()
        results, errors = self.store_results_and_errors(request_id)

        assert_equals(self.storage.count_errors(request_id), len(errors))

    def test_counts_results_and_errors(self):
        f, args, request_id = self.add_request()
        results, errors = self.store_results_and_errors(request_id)

        s = len(results) + len(errors)
        assert_equals(self.storage.count_results_and_errors(request_id), s)

    def test_counts_tasks(self):
        f, args, request_id = self.add_request()
        assert_equals(self.storage.count_tasks(request_id), len(args))
