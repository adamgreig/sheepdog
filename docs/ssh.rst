SSH
===

Sheepdog uses SSH to connect to the GridEngine cluster head. There are a few
issues that may come up in the process.

SSH Keys
--------

Sheepdog will only use SSH keys to connect to the remote server. If you don't
already have these set up, it is simple to do so:

.. code-block:: console

    local$ ssh-keygen
    local$ ssh-copy-id remote

Additionally the keys should either be passphraseless (inadvisable) or stored
in an SSH agent, which Sheepdog will use automatically. Most operating systems
will automatically set up an SSH agent for you, and you can either connect to
the host manually to add the key to the agent, or use ``ssh-add``.

Sheepdog will automatically find a key named `id_rsa` or `id_rsa` in `~/.ssh`,
or you can set `ssh_keyfile` to a path to the (passphraseless) key file to
use. The best way is still to use an SSH agent, though!

Known Hosts
-----------

Sheepdog uses `Paramiko <https://github.com/paramiko/paramiko/>`_ to connect to
SSH servers, and instructs it to read your ~/.ssh/known_hosts file to collect
information on host keys. It does not permit it to connect without a valid
known host key.

However this can cause issues on remote hosts which use ECDSA keys and also
offer an RSA key. In this case Paramiko will (at time of writing) request the
RSA key, fail to find it in your known_hosts (which is likely to only contain
the ECDSA key) and refuse to connect to the server.

One workaround for this problem is to fetch the RSA key of the server and place
it into your known_hosts, for instance:

.. code-block:: console

    local$ ssh remote ssh-keyscan -t rsa remote >> ~/.ssh/known_hosts
    local$ ssh-keygen -H

SSH Config
----------

If a file ``~/.ssh/config`` exists, Sheepdog will use Paramiko to read this
file and use it to determine hostnames, usernames and ports to connect to.
In addition, ProxyCommand directives will also be followed. No other
configuration parameters are used.

If a hostname, username or port is found in the SSH config that matches the
provided hostname, they will be used in preference to the ``ssh_user`` and
``ssh_port`` configuration options.
