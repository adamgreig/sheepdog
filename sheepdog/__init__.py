# Sheepdog
# Copyright 2013, 2014 Adam Greig
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

from __future__ import print_function

__author__ = "Adam Greig <adam@adamgreig.com>"
__version__ = "0.1.10"
__version_info__ = tuple([int(d) for d in __version__.split(".")])
__license__ = "MIT License"

import os
import sys
import time
import copy
import string
import socket
import random
import getpass

from sheepdog.server import get_server
from sheepdog.storage import Storage
from sheepdog.deployment import Deployer
from sheepdog.job_file import job_file

from sheepdog import serialisation

default_config = {
    "ssh_port": 22,
    "ssh_user": getpass.getuser(),
    "ssh_keyfile": None,
    "ssh_dir": ".sheepdog",
    "dbfile": "./sheepdog.sqlite",
    "port": None,
    "ge_opts": ["-wd $HOME/.sheepdog/", "-o $HOME/.sheepdog/",
                "-e $HOME/.sheepdog/"],
    "shell": "/usr/bin/python",
    "localhost": socket.getfqdn()
}


def map_async(f, args, config, ns=None):
    """Submit *f* with each of *args* on GridEngine, returning the
       (sheepdog-local) request ID.
       
       For details on *config*, see the documentation at:
       http://sheepdog.readthedocs.org/en/latest/configuration.html
       Or in docs/configuration.rst.

       Optionally *ns* is a dict containing a namespace to execute the function
       in, which may itself contain additional functions.
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

    password = ''.join(random.choice(string.ascii_letters) for _ in range(30))

    server = get_server(conf['port'], password, conf['dbfile'])
    port = server.port
    url = "http://{0}:{1}/".format(conf['localhost'], port)

    n_args = len(args)
    jf = job_file(url, password, request_id, n_args,
                  conf['shell'], conf['ge_opts'])

    deployer = Deployer(
        conf['host'], conf['ssh_port'], conf['ssh_user'], conf['ssh_keyfile'])
    deployer.deploy(jf, request_id, conf['ssh_dir'])
    deployer.submit(request_id, conf['ssh_dir'])

    return request_id

def get_results(request_id, block=True, verbose=False):
    """Fetch results for *request_id*. If *block* is true, wait until all the
    results are in. Otherwise, return just what has been received so far.

    If *verbose* is true, print a status message every second with the current
    number of results.

    Returns a list of (arg, result) tuples.
    """
    n_args = storage.count_tasks(request_id)
    n_results = 0
    while True:
        n_results = storage.count_results(request_id)
        if verbose:
            print("{}/{} results\r".format(n_results, n_args), flush=True)
        if block:
            break
        time.sleep(1)

    results = []
    for result in storage.get_results(request_id):
        results.append((
            serialisation.deserialise_pickle(r[0]),
            serialisation.deserialise_pickle(r[1])))

    return results

def map(f, args, config, ns=None, verbose=True):
    """Submit *f* with each of *args* on GridEngine, wait until all the results
       are in, and return them in the same order as *args*.
       
       For details on *config*, see the documentation at:
       http://sheepdog.readthedocs.org/en/latest/configuration.html
       Or in docs/configuration.rst.

       Optionally *ns* is a dict containing a namespace to execute the function
       in, which may itself contain additional functions.

       If *verbose* is true, print out how many results are in so-far while
       waiting.
    """
    request_id = map_async(f, args, config, ns)
    return get_results(request_id, block=True, verbose=True)
