"""
Sheepdog
Copyright 2013 Adam Greig

Released under the MIT license. See LICENSE file for details.

HTTP server code.
"""

import json
import base64
from multiprocessing import Process
from flask import Flask, request, g
from sheepdog.dog.storage import Storage

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
    storage = get_storage()
    request_id = int(request.args['request_id'])
    job_index = int(request.args['job_index'])
    details = storage.get_details(request_id, job_index)
    func = base64.b64encode(details[0]).decode()
    args = base64.b64encode(details[1]).decode()
    return json.dumps({"func": func, "args": args})

@app.route('/', methods=['POST'])
def submit_result():
    storage = get_storage()
    request_id = int(request.form['request_id'])
    job_index = int(request.form['job_index'])
    result = base64.b64decode(request.form['result'])
    storage.store_result(request_id, job_index, result)
    return "OK"

@app.route('/error', methods=['POST'])
def report_error():
    storage = get_storage()
    request_id = int(request.form['request_id'])
    job_index = int(request.form['job_index'])
    error = str(request.form['error'])
    storage.store_error(request_id, job_index, error)
    return "OK"

def get_storage():
    if not hasattr(g, '_storage'):
        dbfile = app.config['DBFILE']
        g._storage = Storage(dbfile) if dbfile else Storage()
    return g._storage

def run_server(port=7676, dbfile=None):
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
