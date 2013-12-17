# Sheepdog
# Copyright 2013 Adam Greig
#
# Released under the MIT license. See LICENSE file for details.

"""
Sheepdog's HTTP server endpoints.

The Server class sets up a server on another subprocess, ready to receive
requests from workers. Uses Tornado if available, else falls back to the Flask
debug web server.
"""

import json
import base64
from multiprocessing import Process
from flask import Flask, request, g
from sheepdog.storage import Storage

try:
    from tornado.wsgi import WSGIContainer
    from tornado.httpserver import HTTPServer
    from tornado.ioloop import IOLoop
    USE_TORNADO = True
except ImportError:
    USE_TORNADO = False

app = Flask(__name__)

@app.route('/', methods=['GET'])
def get_config():
    """Endpoint for workers to fetch their configuration before execution.
       Workers should specify `request_id` (integer) and `job_index` (integer)
       from their job file.

       Returns a JSON object:
       
       {"func": (base64 encoded serialised function object),
        "args": (base64 encoded serialised arguments list)
       }

       with HTTP status 200 on success.
    """
    storage = get_storage()
    request_id = int(request.args['request_id'])
    job_index = int(request.args['job_index'])
    details = storage.get_details(request_id, job_index)
    func = base64.b64encode(details[0]).decode()
    args = base64.b64encode(details[1]).decode()
    return json.dumps({"func": func, "args": args})

@app.route('/', methods=['POST'])
def submit_result():
    """Endpoint for workers to submit results arising from successful function
       execution. Should specify `request_id` (integer), `job_index` (integer)
       and `result` (base64 encoded serialised result) HTTP POST parameters.

       Returns the string "OK" and HTTP 200 on success.
    """
    storage = get_storage()
    request_id = int(request.form['request_id'])
    job_index = int(request.form['job_index'])
    result = base64.b64decode(request.form['result'])
    storage.store_result(request_id, job_index, result)
    return "OK"

@app.route('/error', methods=['POST'])
def report_error():
    """Endpoint for workers to report back errors in function execution.
       Workers should specify `request_id` (integer), `job_index` (integer) and
       `error` (an error string) HTTP POST parameters.

       Returns the string "OK" and HTTP 200 on success.
    """
    storage = get_storage()
    request_id = int(request.form['request_id'])
    job_index = int(request.form['job_index'])
    error = str(request.form['error'])
    storage.store_error(request_id, job_index, error)
    return "OK"

def get_storage():
    """Retrieve the request-local database connection, creating it if required.
    """
    if not hasattr(g, '_storage'):
        dbfile = app.config['DBFILE']
        g._storage = Storage(dbfile) if dbfile else Storage()
    return g._storage

def run_server(port=7676, dbfile=None):
    """Start up the HTTP server. If Tornado is available it will be used, else
       fall back to the Flask debug server.
    """
    app.config['DBFILE'] = dbfile
    if USE_TORNADO:
        http_server = HTTPServer(WSGIContainer(app))
        http_server.listen(port)
        IOLoop.instance().start()
    else:
        app.run(host='0.0.0.0', port=port)


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
