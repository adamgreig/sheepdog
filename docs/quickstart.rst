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
the path to it) which must have `Requests <python-requests.org>`_ available.

The cluster workers must be able to connect to the computer running Sheepdog on
a TCP port (default 7676 but may be specified).

Your GridEngine must support array jobs (the -t command).

The ``fear`` GridEngine Cluster
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you're also using ``fear``, put this in your ``.bashrc``::

    source /usr/local/grid/divf2/common/settings.sh

You'll need to have a Python with Requests available (for now at least).
Considering using a virtualenv with the system Python 2.7 or 3.2, or build
your own Python 3.3. Endless fun awaits.

Local Python
^^^^^^^^^^^^

Locally you must have  `Flask <http://flask.pocoo.org/>`_ installed. If you
have `Tornado <http://www.tornadoweb.org/>`_ installed it will be used instead
of the Flask debug server, as it is faster and better. To run tests
`Nose <https://nose.readthedocs.org>`_ is required, and Requests must be
installed locally as well.

Synchronous Map
---------------

In the simplest case you have some function ``f(x1, x2, ...)`` and you wish to
run it with many arguments, ``[(a1, a2, ...), (b1, b2, ...), ...]`` and get
back the results, ``[f(a1, a2, ...), f(b1, b2, ...), ...]``. If the results are
likely to come in quickly and/or you just want to wait for them, use
:py:func:`sheepdog.map_sync`.

Here's what it looks like:

.. code-block:: python

    >>> import sheepdog
    >>> def f(a, b):
    ...    return a + b
    ...
    >>> args = [(1, 1), (1, 2), (2, 2)]
    >>> conf = {"host": "fear"}
    >>> sheepdog.map_sync(f, args, conf)
    [2, 3, 4]
