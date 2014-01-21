The Configuration Object
========================

The ``config`` dictionary passed to the top level functions controls how
Sheepdog behaves. These are the available options:

SSH Options
-----------

``host`` **(required)**
^^^^^^^^^^^^^^^^^^^^^^^
The hostname to submit GridEngine jobs to. This is the server you normally SSH
into to run ``qsub`` etc.

This must be specified and has no default value.

``ssh_port``
^^^^^^^^^^^^
The SSH port to connect to. Defaults to 22.

``ssh_user``
^^^^^^^^^^^^
The username to connect with. Defaults to the current system user.

``ssh_dir``
^^^^^^^^^^^
The remote directory to place job scripts in. Defaults to ``~/.sheepdog``.

Local Server Options
--------------------

``dbfile``
^^^^^^^^^^
The file (or path) to store the sqlite database in. Since results are kept
between requests in case you want to get them later, it might be nice to have
database per set of related projects. Or per project. Or per request, whatever.

Defaults to ``./sheepdog.sqlite``.

``port``
^^^^^^^^
The port that the local HTTP server will listen on. The GridEngine clients must
be able to connect to the local computer on this port.

Defaults to 7676.

``localhost``
^^^^^^^^^^^^^
The hostname by which GridEngine workers may contact the local server. Defaults
to the local FQDN (which really should work!)

GridEngine Options
------------------

``shell``
^^^^^^^^^
A string containing the Python interpreter to use to execute the script. This
is passed to the GridEngine -S option and placed on the script shebang.

Should be a Python binary which the GridEngine worker can execute.

Defaults to ``/usr/bin/env python3``.

``ge_opts``
^^^^^^^^^^^
A list of strings containing GridEngine options. This is used to specify
additional GridEngine related arguments, for example ``-l ubuntu=1`` to specify
a resource requirement or ``-r y`` to specify that the job may be re-run.

If unspecified defaults to ``["-r y", "-l ubuntu=1", "-l lr=0"]`` which is
particularly helpful on ``fear`` and shouldn't be too adverse elsewhere.

Note that ``-S /path/to/shell`` is always specified by the ``shell`` option
detailed above, and ``-t 1-N`` is always specified with N equal to the number
of arguments being evaluated.

All these options are written to the top of the job file which is copied to the
GridEngine server, so may be inspected manually too.
