Quickstart
==========

Woof woof!

Requirements
------------

A GridEngine Cluster
^^^^^^^^^^^^^^^^^^^^

Your cluster must have some *head* node, which is the node you connect to
when you want to run ``qsub``. Here we'll use the name ``fear``, because that
is the name of the author's head node.

The head node must be able to run ``qsub`` and you must be able to SSH into
it. This might require having GridEngine stuff in your ``.bashrc``, so that
``ssh fear qstat -F no`` actually works.

The cluster workers must be able to run a Python interpreter (you can specify
the path if you wish to use a custom interpreter).

The cluster workers must be able to connect to the computer running Sheepdog on
a TCP port (defaults to a random available port but may be specified).

Your GridEngine must support array jobs (the -t command).

The ``fear`` GridEngine Cluster
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you're also using ``fear``, put this in your ``.bashrc``::

    source /usr/local/grid/divf2/common/settings.sh

Local Python
^^^^^^^^^^^^

Locally you must have  `Flask <http://flask.pocoo.org/>`_ and
`Paramiko <https://github.com/paramiko/paramiko>`_ installed. If you have
`Tornado <http://www.tornadoweb.org/>`_ installed it will be used instead of
the Flask debug server, as it is faster and better. To run tests
`Nose <https://nose.readthedocs.org>`_ is required.

Synchronous Map
---------------

In the simplest case you have some function ``f(x1, x2, ...)`` and you wish to
run it with many arguments, ``[(a1, a2, ...), (b1, b2, ...), ...]`` and get
back the results, ``[f(a1, a2, ...), f(b1, b2, ...), ...]``. If the results are
likely to come in quickly and/or you just want to wait for them, use
:py:func:`sheepdog.map`.

Here's what it looks like:

.. code-block:: python

    >>> import sheepdog
    >>> def f(a, b):
    ...    return a + b
    ...
    >>> args = [(1, 1), (1, 2), (2, 2)]
    >>> conf = {"host": "fear", "ge_opts": ["-l ubuntu=1", "-l lr=0"]}
    >>> sheepdog.map(f, args, conf)
    [2, 3, 4]

Asynchronous Map
----------------

Much like :py:func:`sheepdog.map`, :py:func:`sheepdog.map_async` runs ``f``
with each set of arguments in ``args`` using the provided configuration and
optional namespace. Unlike :py:func:`sheepdog.map`,
:py:func:`sheepdog.map_async` returns a request ID immediately after
deployment, and it is then up to the user to poll for status, for example using
:py:func:`sheepdog.get_results`.

Namespaces
----------

Often the target function will require other items be present in its namespace,
for instance constants or other functions. These may be passed in the namespace
parameter `ns` of map:

.. code-block:: python

    >>> import sheepdog
    >>> constant = 12
    >>> def g(x):
    ...     return x * 2
    ...
    >>> def f(a, b):
    ...     return a + g(b) + constant
    ...
    >>> args = [(1, 2), (2, 3), (3, 4)]
    >>> conf = {"host": "fear"}
    >>> namespace = {"constant": constant, "g": g}
    >>> sheepdog.map_sync(f, args, conf)
    [17, 20, 23] 

Imports
-------

Sheepdog doesn't currently provide for automatic handling of imports and
dependencies. Please ensure that all required Python packages are available on
the execution hosts. To actually run the import, put it at the top of your
function, optionally exporting the package so that other functions can use it.

For example:

.. code-block:: python

    >>> def g(x):
    ...     return np.mean(x)
    ...
    >>> def f(x):
    ...     import numpy as np
    ...     global np
    ...     return g(x)
    ...


Results and Errors
------------------

To fetch results out of the database after a request, see
:py:func:`sheepdog.get_results`. Similarly for errors that may have occured
during the job (those that Python was able to catch and recover from), you can
use :py:func:`sheepdog.get_errors`. If errors were detected and verbose mode is
on, you will also be prompted to check the errors after calling
:py:func:`sheepdog.map`.
