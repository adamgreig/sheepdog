"""
Sheepdog
Copyright 2013 Adam Greig

Released under the MIT license. See LICENSE file for details.

Glue it all together.
"""

import os
import sys
import time
import copy
import socket
import marshal

from sheepdog.dog.server import Server
from sheepdog.dog.storage import Storage
from sheepdog.dog.deployment import deploy_and_run
from sheepdog.sheep.job_file import job_file

default_config = {
    "ssh_port": 22,
    "ssh_user": os.getlogin(),
    "dbfile": "./sheepdog.sqlite",
    "port": 7676,
    "ge_opts": [],
    "shell": "/usr/bin/env python3",
    "localhost": socket.getfqdn()
}


def map_sync(f, args, config):
    """Run *f* with each of *args* on GridEngine and return the results.
       
       Blocks until all results are in.

       *config* must be a dict including:
            `host`: the hostname to submit grid engine jobs to [required]
            `ssh_port`: the ssh port to connect on
            `ssh_user`: the ssh username to use
            `dbfile`: the filename for the results db
            `port`: the port for the server to listen on
            `ge_opts`: a list of grid engine options
            `shell`: the path to the python to run the job with
            `localhost`: the hostname for workers to find the local host
    """

    conf = copy.copy(default_config)
    conf.update(config)
    func_bin = marshal.dumps(f.__code__)
    args_bin = [marshal.dumps(arg) for arg in args]
    storage = Storage(dbfile=conf['dbfile'])
    storage.initdb()
    request_id = storage.new_request(func_bin, args_bin)
    server = Server(port=conf['port'], dbfile=conf['dbfile'])
    url = "http://{0}:{1}/".format(conf['localhost'], conf['port'])
    n_args = len(args)
    jf = job_file(url, request_id, n_args, conf['ge_opts'], conf['shell'])
    print("Deploying job with request ID {0}...".format(request_id))
    deploy_and_run(conf['host'], jf, request_id,
                   conf['ssh_user'], conf['ssh_port'])

    n_results = 0
    while n_results != n_args:
        n_results = storage.count_results(request_id)
        sys.stdout.write("Received {0}/{1} results...\r".format(
            n_results, n_args))
        sys.stdout.flush()
        time.sleep(1)

    return [marshal.loads(r[1]) for r in storage.get_results(request_id)]
