"""
Sheepdog
Copyright 2013 Adam Greig

Server storage stuff.
"""

import sqlite3

schema = """
CREATE TABLE IF NOT EXISTS requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    function BLOB,
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
    id INTEGER INTEGER PRIMARY KEY,
    task_id INTEGER,
    result BLOB,
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
        c.close()

    def new_request(self, serialised_function, args_list):
        """Add a new request to the database.

        serialised_function is some bytes object that should be given to
        workers to turn into the code to execute, for instance marshalled
        bytecode, or a string to compile.

        args_list is a list, tuple or other iterable where each item is
        some bytes object that should be given to workers to run their
        target function with. Probably a marshalled tuple or similar.
        """
        c = self.conn.cursor()
        c.execute("INSERT INTO requests (function, date_submitted)"
                  " VALUES (?, date('now'))", (serialised_function,))
        request_id = c.lastrowid
        tasks_list = []
        for idx, arg in enumerate(args_list):
            tasks_list.append((request_id, idx + 1, arg))
        c.executemany("INSERT INTO tasks (request_id, job_index, args)"
                      " VALUES (?, ?, ?)", tasks_list)
        self.conn.commit()
        c.close()

    def get_details(self, request_id, job_index):
        """Get the target function and arguments for a given job index.
        """
        c = self.conn.cursor()
        c.execute("SELECT requests.function, tasks.args FROM tasks"
                  " JOIN requests ON tasks.request_id=requests.id"
                  " WHERE request_id=? AND job_index=?",
                  (request_id, job_index))
        details = c.fetchone()
        if not details:
            raise ValueError("No details found for specified request and job.")
        c.close()
        return details

    def store_result(self, request_id, job_index, result):
        """Store a new result from a given request_id and job_index."""
        c = self.conn.cursor()
        c.execute("SELECT id FROM tasks"
                  " WHERE request_id=? AND job_index=?",
                  (request_id, job_index))
        task_id = c.fetchone()
        if not task_id:
            c.close()
            raise ValueError("No task found for specified request and job.")
        c.execute("INSERT INTO results (task_id, result) VALUES (?, ?)",
                  (task_id[0], result))
        self.conn.commit()
        c.close()

    def get_results(self, request_id):
        """Fetch all results for a given request_id.

        Returns a list of (args, result) items in the order of the original
        args_list provided to new_request.
        """
        c = self.conn.cursor()
        c.execute("SELECT tasks.args, results.result"
                  " FROM results"
                  " JOIN tasks ON results.task_id=tasks.id"
                  " WHERE tasks.request_id=?"
                  " ORDER BY tasks.job_index", (request_id,))
        return c.fetchall()
