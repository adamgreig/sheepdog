# Sheepdog
# Copyright 2013 Adam Greig
#
# Released under the MIT license. See LICENSE file for details.

"""
Interface to the storage backend.

Future plans involve porting most of those handwritten SQL to a sensible ORM.
"""

import sqlite3

schema = """
CREATE TABLE IF NOT EXISTS requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    function BLOB,
    namespace BLOB,
    date_submitted TEXT
);

CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    request_id INTEGER,
    job_index INTEGER,
    args BLOB,
    FOREIGN KEY (request_id) REFERENCES requests(id)
);

CREATE TABLE IF NOT EXISTS results (
    id INTEGER PRIMARY KEY,
    task_id INTEGER,
    result BLOB,
    FOREIGN KEY (task_id) REFERENCES tasks(id)
);

CREATE TABLE IF NOT EXISTS errors (
    id INTEGER PRIMARY KEY,
    task_id INTEGER,
    error TEXT,
    FOREIGN KEY (task_id) REFERENCES tasks(id)
);
"""

class Storage:
    """Manage persistence for requests and results.

    Request functions and result objects are stored as binary
    blobs in the database, so any bytes object will be fine.
    They'll be returned as they were sent.

    """

    def __init__(self, dbfile="./sheepdog.sqlite"):
        """__init__ creates a database connection.

        dbfile is a file path for the sqlite file, or `:memory:` to only
        use in memory persistence.
        """
        self.dbfile = dbfile
        self.conn = sqlite3.connect(dbfile)

    def initdb(self):
        """Create the database structure if it doesn't already exist.
        """
        c = self.conn.cursor()
        c.executescript(schema)
        self.conn.commit()

    def new_request(self, serialised_function, serialised_namespace,
                    args_list):
        """Add a new request to the database.

        serialised_function is some bytes object that should be given to
        workers to turn into the code to execute.

        serialised_namespace is some bytes object that should be given to
        workers alongside the serialised function to provide helper variables
        and functions that the primary function requires.

        args_list is a list, tuple or other iterable where each item is
        some bytes object that should be given to workers to run their
        target function with.

        Returns the new request ID.
        """
        c = self.conn.cursor()
        c.execute("INSERT INTO requests (function, namespace, date_submitted)"
                  " VALUES (?, ?, date('now'))",
                  (sqlite3.Binary(serialised_function),
                   sqlite3.Binary(serialised_namespace)))
        request_id = c.lastrowid
        tasks_list = []
        for idx, arg in enumerate(args_list):
            tasks_list.append((request_id, idx + 1, sqlite3.Binary(arg)))
        c.executemany("INSERT INTO tasks (request_id, job_index, args)"
                      " VALUES (?, ?, ?)", tasks_list)
        self.conn.commit()
        return request_id

    def get_details(self, request_id, job_index):
        """Get the target function, namespace and arguments for a given job.
        """
        c = self.conn.cursor()
        c.execute("SELECT requests.function, requests.namespace, tasks.args"
                  " FROM tasks"
                  " JOIN requests ON tasks.request_id=requests.id"
                  " WHERE request_id=? AND job_index=?",
                  (request_id, job_index))
        details = c.fetchone()
        if not details:
            raise ValueError("No details found for specified request and job.")
        return (bytes(details[0]), bytes(details[1]), bytes(details[2]))

    def _get_task_id(self, request_id, job_index):
        """Retrieve the task ID for a given request ID and job index."""
        c = self.conn.cursor()
        c.execute("SELECT id FROM tasks"
                  " WHERE request_id=? AND job_index=?",
                  (request_id, job_index))
        task_id = c.fetchone()
        if not task_id:
            raise ValueError("No task found for specified request and job.")
        return task_id[0]

    def store_result(self, request_id, job_index, result):
        """Store a new result from a given request_id and job_index."""
        task_id = self._get_task_id(request_id, job_index)
        c = self.conn.cursor()
        c.execute("INSERT INTO results (task_id, result) VALUES (?, ?)",
                  (task_id, sqlite3.Binary(result)))
        self.conn.commit()

    def store_error(self, request_id, job_index, error):
        """Store an error resulting from a computation."""
        task_id = self._get_task_id(request_id, job_index)
        c = self.conn.cursor()
        c.execute("INSERT INTO errors (task_id, error) VALUES (?, ?)",
                  (task_id, error))
        self.conn.commit()

    def count_results(self, request_id):
        """Count the number of results so far for the given request_id."""
        c = self.conn.cursor()
        c.execute("SELECT COUNT(*)"
                  " FROM results"
                  " JOIN tasks ON results.task_id=tasks.id"
                  " WHERE tasks.request_id=?", (request_id,))
        return c.fetchone()[0]

    def count_errors(self, request_id):
        """Count the number of errors reported so far."""
        c = self.conn.cursor()
        c.execute("SELECT COUNT(*)"
                  " FROM errors"
                  " JOIN tasks ON errors.task_id=tasks.id"
                  " WHERE tasks.request_id=?", (request_id,))
        return c.fetchone()[0]

    def count_results_and_errors(self, request_id):
        """Sum the result and error counts."""
        return self.count_results(request_id) + self.count_errors(request_id)

    def count_tasks(self, request_id):
        """Count the total number of tasks for this request."""
        c = self.conn.cursor()
        c.execute("SELECT COUNT(*) FROM tasks WHERE tasks.request_id=?",
                  (request_id,))
        return c.fetchone()[0]

    def get_results(self, request_id):
        """Fetch all results for a given request_id.

        Returns a list of (args, result) items in the order of the original
        args_list provided to new_request.

        Gaps are not filled in, so if results have not yet been submitted
        the corresponding arguments will not appear in this list and this
        list will be shorter than the length of args_list.
        """
        c = self.conn.cursor()
        c.execute("SELECT tasks.args, results.result"
                  " FROM results"
                  " JOIN tasks ON results.task_id=tasks.id"
                  " WHERE tasks.request_id=?"
                  " ORDER BY tasks.job_index", (request_id,))
        return [(bytes(r[0]), bytes(r[1])) for r in c.fetchall()]

    def get_errors(self, request_id):
        """Fetch all errors for a given request_id.

        Returns a list of (args, error) items in the order of the original
        args_list provided to new_request.
        """
        c = self.conn.cursor()
        c.execute("SELECT tasks.args, errors.error"
                  " FROM errors"
                  " JOIN tasks ON errors.task_id=tasks.id"
                  " WHERE tasks.request_id=?"
                  " ORDER BY tasks.job_index", (request_id,))
        return [(bytes(r[0]), r[1]) for r in c.fetchall()]
