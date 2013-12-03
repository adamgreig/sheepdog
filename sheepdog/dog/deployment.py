"""
Sheepdog
Copyright 2013 Adam Greig

Deployment code.
"""

# All I want for Christmas is Python 3 support in Paramiko.
# Until then...

import os
import tempfile
import subprocess

def deploy_and_run(host, jobfile, request_id, user=None, port=22):
    """Deploy *jobfile* to *host*, using *request_id* to name it, then
       submit it to the GridEngine queue.
    """
    if user is None:
        user = os.getlogin()

    hoststr = "{0}@{1}:{2}".format(user, host, port)
    filestr = "{0}:~/sheepdog_{1}.py".format(hoststr, request_id)
    cmdstr = "qsub ~/sheepdog_{0}.py".format(request_id)

    fd, fp = tempfile.mkstemp()
    os.write(fd, jobfile)

    rv = subprocess.call(["scp", fp, filestr])

    os.close(fd)
    os.unlink(fp)

    if rv:
        raise RuntimeError("Error uploading job file.")

    rv = subprocess.call(["ssh", hoststr, cmdstr])

    if rv:
        raise RuntimeError("Error submitting job request.")
