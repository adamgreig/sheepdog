# Sheepdog
# Copyright 2013 Adam Greig
#
# Released under the MIT license. See LICENSE file for details.

"""
Generate job files to send to the cluster.

The template is filled in with the job specifics and the formatted string is
returned ready for deployment.
"""

import inspect
from sheepdog import client, serialisation

template = """#!{shell}
{geopts}

# Sheepdog Job File
# Autogenerated by Sheepdog. Don't edit by hand.
# See https://github.com/adamgreig/sheepdog

###########################################################
## Serialisation code from Sheepdog:

{serialisation_code}

##
###########################################################

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
    """Format the template for a specific job, ready for deployment.
       
       *url* is the URL (including port) that the workers should contact to
       fetch job information, including a trailing slash.

       *request_id* is the request ID workers should use to associate
       themselves with the correct request.

       *n_args* is the number of jobs that will be queued in the array task,
       the same as the number of arguments being mapped by sheepdog.

       *grid_engine_opts* is a list of string arguments to Grid Engine to
       specify options such as resource requirements. Defaults to "-r y", "-l
       ubuntu=1" and "-l lr=0".

       *shell* is the path to the Python that will execute the job. Could be a
       system or user Python, so long as it meets the Sheepdog requirements.
       Is used for the -S option to GridEngine as well as the script shebang.
    """
    if not grid_engine_opts:
        grid_engine_opts = ["-r y", "-l ubuntu=1", "-l lr=0"]
    if not shell:
        shell = "/usr/bin/env python3"
    grid_engine_opts.append("-t 1-{0}".format(n_args))
    grid_engine_opts.append("-S {0}".format(shell))
    geopts = '\n'.join("#$ {0}".format(opt) for opt in grid_engine_opts)
    client_code = inspect.getsource(client)
    serialisation_code = inspect.getsource(serialisation)
    return template.format(**locals())
