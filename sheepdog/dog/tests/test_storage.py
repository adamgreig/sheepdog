"""
Sheepdog
Copyright 2013 Adam Greig

Storage tests.
"""

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
        self.storage.new_request(f, args)

        return f, args

    def test_adds_request(self):
        f, args = self.add_request()

        self.c.execute("SELECT * FROM requests")
        request = self.c.fetchone()
        assert_equals(request[1], f)

        self.c.execute("SELECT request_id, job_index, args FROM tasks")
        tasks = self.c.fetchall()
        assert_equals(len(tasks), 3)
        assert_equals(tasks[0], (request[0], 1, args[0]))
        assert_equals(tasks[1], (request[0], 2, args[1]))
        assert_equals(tasks[2], (request[0], 3, args[2]))

    def test_gets_details(self):
        f, args = self.add_request()
        
        request_id = self.c.execute("SELECT MAX(id) FROM requests").fetchone()
        details = self.storage.get_details(request_id[0], 2)
        assert_equals(details, (f, args[1]))

    def store_results(self):
        results = [b"ABC", b"DEF", b"GEH"]
        request_id = self.c.execute("SELECT MAX(id) FROM requests").fetchone()
        for idx, result in enumerate(results):
            self.storage.store_result(request_id[0], idx+1, result)
        return results

    def test_stores_results(self):
        f, args = self.add_request()
        results = self.store_results()

        r = self.c.execute("SELECT task_id, result FROM results").fetchall()
        assert_equals(r[0][1], results[0])
        assert_equals(r[1][1], results[1])
        assert_equals(r[2][1], results[2])

        self.c.execute("SELECT request_id, job_index FROM tasks"
                       " WHERE id=?", (r[1][0],))
        r = self.c.fetchone()
        assert_equals(r[1], 2)

    def test_gets_results(self):
        f, args = self.add_request()
        results = self.store_results()
        
        request_id = self.c.execute("SELECT MAX(id) FROM requests").fetchone()
        r = self.storage.get_results(request_id[0])

        assert_equals(r, list(zip(args, results)))
