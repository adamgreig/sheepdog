# Sheepdog
# Copyright 2013 Adam Greig
#
# Released under the MIT license. See LICENSE file for details.

"""
Sheepdog is a utility to run arbitary code on a GridEngine cluster and collect
the results, typically by mapping a set of arguments to one function.

Documentation: http://sheepdog.readthedocs.org

Source code: https://github.com/adamgreig/sheepdog

PyPI: https://pypi.python.org/pypi/Sheepdog

Sheepdog is released under the MIT license, see the LICENSE file for details.
"""

__author__ = "Adam Greig <adam@adamgreig.com>"
__version__ = "0.1.6"
__version_info__ = tuple([int(d) for d in __version__.split(".")])
__license__ = "MIT License"

import os
import sys
import time
import copy
import socket
import getpass

from sheepdog.server import Server
from sheepdog.storage import Storage
from sheepdog.deployment import deploy_and_run
from sheepdog.job_file import job_file

from sheepdog import serialisation

default_config = {
    "ssh_port": 22,
    "ssh_user": getpass.getuser(),
    "ssh_dir": "$HOME/.sheepdog",
    "dbfile": "./sheepdog.sqlite",
    "port": 7676,
    "ge_opts": ["-r y", "-l ubuntu=1", "-l lr=0", "-wd $HOME/.sheepdog/",
                "-o $HOME/.sheepdog/", "-e $HOME/.sheepdog/"],
    "shell": "/usr/bin/python",
    "localhost": socket.getfqdn()
}


def map_sync(f, args, config, ns=None):
    """Run *f* with each of *args* on GridEngine and return the results.

       Optionally *ns* is a dict containing a namespace to execute the function
       in, which may itself contain additional functions.
       
       Blocks until all results are in.

       *config* must be a dict including:

            `host`: the hostname to submit grid engine jobs to [required]

            `ssh_port`: the ssh port to connect on
                        (default: 22)

            `ssh_user`: the ssh username to use
                        (default: current username)

            `ssh_dir`: the remote directory to put job scripts in
                       (default $HOME/.sheepdog)

            `dbfile`: the filename for the results db
                      (default ./sheepdog.sqlite)

            `port`: the port for the server to listen on
                    (default: 7676)

            `ge_opts`: a list of grid engine options
                       (default: ["-r y", "-l ubuntu=1", "-l lr=0",
                                  "-wd $HOME/.sheepdog/",
                                  "-o $HOME/.sheepdog/",
                                  "-e $HOME/.sheepdog/"])

            `shell`: the path to the python to run the job with
                     (default: "/usr/bin/python")

            `localhost`: the hostname for workers to find the local host
                         (default: system's FQDN)
    """
    if not ns:
        ns = {}

    conf = copy.copy(default_config)
    conf.update(config)
    func_bin = serialisation.serialise_function(f)
    args_bin = serialisation.serialise_args(args)
    namespace_bin = serialisation.serialise_namespace(ns)
    storage = Storage(dbfile=conf['dbfile'])
    storage.initdb()
    request_id = storage.new_request(func_bin, namespace_bin, args_bin)
    server = Server(port=conf['port'], dbfile=conf['dbfile'])
    url = "http://{0}:{1}/".format(conf['localhost'], conf['port'])
    n_args = len(args)
    jf = job_file(url, request_id, n_args, conf['shell'], conf['ge_opts'])
    print("Deploying job with request ID {0}...".format(request_id))
    deploy_and_run(conf['host'], jf, request_id,
                   conf['ssh_user'], conf['ssh_port'], conf['ssh_dir'])

    n_results = 0
    while n_results != n_args:
        n_results = storage.count_results(request_id)
        sys.stdout.write("Received {0}/{1} results...\r".format(
            n_results, n_args))
        sys.stdout.flush()
        time.sleep(1)

    return [serialisation.deserialise_pickle(r[1])
            for r in storage.get_results(request_id)]
