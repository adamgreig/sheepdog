# Sheepdog
# Copyright 2013, 2014 Adam Greig
#
# Released under the MIT license. See LICENSE file for details.

"""
Code for deploying code to servers and executing jobs on GridEngine.
"""

import os.path
import paramiko

class Deployer:
    """Connect to a remote SSH server, copy a file over, run qsub."""

    def __init__(self, host, port, user, keyfile=None):
        """__init__ takes (host, port, user, keyfile) to specify which SSH
           server to connect to and how to connect to it.
        """
        self.host = host
        self.port = port
        self.user = user
        self.keyfile = keyfile
        self.sock = None

        self.ssh = paramiko.SSHClient()
        self.ssh.load_system_host_keys()
        self._process_config()

        self.ssh.connect(self.host, self.port, self.user,
                         key_filename=keyfile, sock=self.sock)

    def deploy(self, jobfile, request_id, directory):
        """Copy *jobfile* (a string of the file contents) to the connected
           remote host, placing it in *directory* with a filename containing
           *request_id*.
        """
        path = self._get_jobfile_path(request_id, directory)
        sftp = self.ssh.open_sftp()

        try:
            sftp.mkdir(directory, mode=0o750)
        except (IOError, OSError):
            pass

        with sftp.open(path, 'w') as f:
            f.write(jobfile)

    def submit(self, request_id, directory):
        """Submit a job to the GridEngine cluster on the connected remote host.
           Calls qsub with the job identified by request_id and directory.
        """
        path = self._get_jobfile_path(request_id, directory)
        si, so, se = self.ssh.exec_command("qsub {}".format(path))
        return so.read()

    def _get_jobfile_path(self, request_id, directory):
        """Put together the path at which the job file for a given *request_id*
           will be found, given *directory*.
        """
        return os.path.join(directory, "sheepdog_{:03}.py".format(request_id))

    def _process_config(self):
        """Parse the user's local ssh config (if any) and use it to update
           the hostname, port and username used for connection.
        """
        config = paramiko.SSHConfig()
        config_path = os.path.expanduser("~/.ssh/config")
        
        try:
            with open(config_path) as f:
                config.parse(f)
        except IOError:
            pass

        host_config = config.lookup(self.host)

        self.host = host_config.get('hostname', self.host)
        self.user = host_config.get('user', self.user)
        self.port = host_config.get('port', self.port)

        if 'proxycommand' in host_config:
            self.sock = paramiko.ProxyCommand(host_config['proxycommand'])
