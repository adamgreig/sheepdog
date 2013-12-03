"""
Sheepdog
Copyright 2013 Adam Greig

HTTP server code.
"""

from json import dumps
from flask import Flask, request, g
from base64 import b64encode, b64decode
from multiprocessing import Process
from sheepdog.dog.storage import Storage

app = Flask(__name__)

@app.route('/', methods=['GET'])
def get_config():
    storage = get_storage()
    request_id = int(request.args['request_id'])
    job_index = int(request.args['job_index'])
    details = storage.get_details(request_id, job_index)
    func = b64encode(details[0]).decode()
    args = b64encode(details[1]).decode()
    return dumps({"func": func, "args": args})

@app.route('/', methods=['POST'])
def submit_result():
    storage = get_storage()
    request_id = int(request.form['request_id'])
    job_index = int(request.form['job_index'])
    result = request.form['result']
    result = b64decode(result)
    storage.store_result(request_id, job_index, result)
    return "OK"

def get_storage():
    if not hasattr(g, '_storage'):
        dbfile = app.config['DBFILE']
        g._storage = Storage(dbfile) if dbfile else Storage()
    return g._storage

def run_server(port=None, dbfile=None):
    app.config['DBFILE'] = dbfile
    app.run(port=port)


class Server:
    """Run the HTTP server for workers to request arguments and return results.
    """

    def __init__(self, port=7676, dbfile=None):
        """__init__ creates and starts the HTTP server.
        """
        self.server = Process(target=run_server, args=(port, dbfile))
        self.server.start()

    def stop(self):
        """Terminate the HTTP server."""
        self.server.terminate()
        self.server.join()

    def __del__(self):
        self.stop()
