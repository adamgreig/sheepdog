# Sheepdog
# Copyright 2013 Adam Greig
#
# Released under the MIT license. See LICENSE file for details.

import inspect
from sheepdog import client

template = """#!{shell}
{geopts}

# Sheepdog Job File
# Autogenerated by Sheepdog. Don't edit by hand.

###########################################################
## Clientside code from Sheepdog:

{client_code}

##
###########################################################

import os
job_index = os.environ['SGE_TASK_ID']
Client("{url}", {request_id}, job_index).go()
"""

def job_file(url, request_id, n_args, grid_engine_opts=None, shell=None):
    if grid_engine_opts is None:
        grid_engine_opts = ["-r y", "-l ubuntu=1", "-l lr=0"]
    if shell is None:
        shell = "/usr/bin/env python3"
    grid_engine_opts.append("-t 1-{0}".format(n_args))
    grid_engine_opts.append("-S {0}".format(shell))
    geopts = '\n'.join("#$ {0}".format(opt) for opt in grid_engine_opts)
    client_code = inspect.getsource(client)
    return template.format(**locals())
