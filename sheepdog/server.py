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
import atexit
import socket
from functools import wraps
from multiprocessing import Process
from flask import Flask, Response, request, g
from sheepdog.storage import Storage

try:
    from tornado.wsgi import WSGIContainer
    from tornado.httpserver import HTTPServer
    from tornado.ioloop import IOLoop
    USE_TORNADO = True
except ImportError:
    USE_TORNADO = False

app = Flask(__name__)

def check_auth(username, password):
    return username == 'sheepdog' and password == app.config['PASSWORD'] 

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return Response("Unauthorized", 401)
        return f(*args, **kwargs)
    return decorated

@app.route('/', methods=['GET'])
@requires_auth
def get_config():
    """Endpoint for workers to fetch their configuration before execution.
       Workers should specify `request_id` (integer) and `job_index` (integer)
       from their job file.

       Returns a JSON object:
       
       {"func": (serialised function object),
        "args": (serialised arguments list)
       }

       with HTTP status 200 on success.
    """
    storage = get_storage()
    request_id = int(request.args['request_id'])
    job_index = int(request.args['job_index'])
    details = storage.get_details(request_id, job_index)
    func = details[0].decode()
    ns = details[1].decode()
    args = details[2].decode()
    return json.dumps({"func": func, "ns": ns, "args": args})

@app.route('/', methods=['POST'])
@requires_auth
def submit_result():
    """Endpoint for workers to submit results arising from successful function
       execution. Should specify `request_id` (integer), `job_index` (integer)
       and `result` (serialised result) HTTP POST parameters.

       Returns the string "OK" and HTTP 200 on success.
    """
    storage = get_storage()
    request_id = int(request.form['request_id'])
    job_index = int(request.form['job_index'])
    result = request.form['result'].encode()
    storage.store_result(request_id, job_index, result)
    return "OK"

@app.route('/error', methods=['POST'])
@requires_auth
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
        g._storage = Storage(dbfile)
    return g._storage

def _get_free_port():
    """Get a port that should be free on the system."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("", 0))
    port = s.getsockname()[1]
    s.close()
    return port

def run_server(port, password, dbfile):
    """Start up the HTTP server. If Tornado is available it will be used, else
       fall back to the Flask debug server.
    """
    app.config['PASSWORD'] = password
    app.config['DBFILE'] = dbfile

    if USE_TORNADO:
        # When running inside an IPython Notebook, the IOLoop
        # can inherit a stale instance from the parent process,
        # so clear that.
        # https://github.com/adamgreig/sheepdog/issues/15
        # Thanks @minrk!
        if hasattr(IOLoop, '_instance'):
            del IOLoop._instance
        IOLoop.clear_current()

        HTTPServer(WSGIContainer(app)).listen(port)
        IOLoop.instance().start()
    else:
        app.run(host='0.0.0.0', port=port)


class Server:
    """Run the HTTP server for workers to request arguments and return results.

       Should be used via get_server(port, password, dbfile) to manage servers
       running globally.
    """

    def __init__(self, port, password, dbfile):
        """__init__ creates and starts the HTTP server.
        """
        if not port:
            port = _get_free_port()
        self.port = port
        self.password = password
        self.dbfile = dbfile
        self.server = Process(target=run_server, args=(port, password, dbfile))
        self.server.start()

    def stop(self):
        """Terminate the HTTP server."""
        self.server.terminate()
        self.server.join()

    def __del__(self):
        self.stop()

_servers = {}
def get_server(port, password, dbfile):
    """Either start a new server or retrieve a reference to an existing server.
       Only one server may run per port. If the server currently running on
       that port has a different password or dbfile, a RuntimeError is raised.

       If `None` is specified for port, a port is picked randomly and that
       server is the one referenced for `None` thereafter.
    """
    global _servers
    if port not in _servers:
        server = Server(port, password, dbfile)
        _servers[port] = server

        # When port is None, this adds another entry for the server on the port
        # it's actually running on
        _servers[server.port] = server
    else:
        server = _servers[port]
        if server.password != password or server.dbfile != dbfile:
            raise RuntimeError("A server is already running on that port with "
                               "a different password or dbfile.")
    return server

def _cleanup_servers():
    """Shut down all running servers in _servers"""
    global _servers
    for port in _servers:
        _servers[port].stop()
    del _servers

# The servers will continue in their subprocess without going out of scope
# if we hold a reference in _servers, so register a handler to get rid of
# them when this process ends.
atexit.register(_cleanup_servers)
