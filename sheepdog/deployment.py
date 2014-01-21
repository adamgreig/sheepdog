# Sheepdog
# Copyright 2013 Adam Greig
#
# Released under the MIT license. See LICENSE file for details.

"""
Code for deploying code to servers and executing jobs on GridEngine.

Right now this is a little unwieldly and uses SSH as a subprocess.
"""

# All I want for Christmas is Python 3 support in Paramiko.
# Until then...

import os
import tempfile
import subprocess

def deploy_and_run(host, jobfile, request_id, user=None, port=22,
                   directory="~/.sheepdog"):
    """Deploy *jobfile* to *host*, using *request_id* to name it, then
       submit it to the GridEngine queue.
    """
    if user is None:
        user = os.getlogin()

    hoststr = "{0}@{1}".format(user, host)
    scpportstr = "-P {0}".format(port)
    sshportstr = "-p {0}".format(port)
    filestr = "{0}:{1}/sheepdog_{2}.py".format(hoststr, directory, request_id)
    mkdirstr = "mkdir -p {0}".format(directory)
    submitstr = "qsub {0}/sheepdog_{1}.py".format(directory, request_id)

    rv = subprocess.call(["ssh", sshportstr, hoststr, mkdirstr])

    if rv:
        raise RuntimeError("Error creating {0}".format(directory))

    fd, fp = tempfile.mkstemp()
    os.write(fd, jobfile.encode())

    rv = subprocess.call(["scp", scpportstr, fp, filestr])

    os.close(fd)
    os.unlink(fp)

    if rv:
        raise RuntimeError("Error uploading job file.")

    rv = subprocess.call(["ssh", sshportstr, hoststr, submitstr])

    if rv:
        raise RuntimeError("Error submitting job request.")
