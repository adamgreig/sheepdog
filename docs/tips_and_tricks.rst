Tips and Tricks
===============

Setting Custom Pickle and Marshal Protocols
-------------------------------------------

By default, Sheepdog uses Pickle protocol `pickle.DEFAULT_PROTOCOL` and marshal
version `marshal.version`. These correlate to the default protocols for your
current Python interpreter.

However, if your worker nodes are running an older Python than the computer
running Sheepdog, you may need to decrease these protocols. For example, Python
3 uses Pickle protocol 3 by default, which is not compatible with any Python 2.

To change this, overwrite `sheepdog.serialisation.pickle_protocol` and
`sheepdog.serialisation.marshal_version`:

.. code-block:: python

    >>> import sheepdog
    >>> sheepdog.serialisation.pickle_protocol = 2
    >>> sheepdog.map_sync(...)

Restarting The Server
---------------------

Should the HTTP server that listens for requests and results from job workers
die, any still-queued jobs will not be able to start, and any currently running
jobs will not be able to submit results. Jobs do send their results to standard
output, but it's obviously better to get a server up again. You don't have to
resubmit the request, instead just start a new Server and keep it around until
the job is complete. Here's an example:

.. code-block:: python

    import sys
    import time
    import sheepdog
    server = sheepdog.Server()
    storage = sheepdog.Storage()
    while True:
        n_results = storage.count_results(int(sys.argv[1]))
        print(n_results, "results\r", flush=True)
        time.sleep(5)

This code gets one request ID from the command line, starts a server (here
using the default location of './sheepdog.sqlite' but you can change this in
the Storage constructor) and waits for results to come in.


Finding Request IDs, Ports and Passwords
----------------------------------------

For getting results out of previously completed jobs you'll need the request
ID, but this isn't obviously found if you're just using the synchronous
:py:func:`sheepdog.map` function. You can find these values by looking in the
Sheepdog job files on the GridEngine server, instead. These files are by
default placed in `~/.sheepdog` and named like `sheepdog_032.py`. The final
line contains a call to Client with the URL, password and request ID:

``Client("http://your.host:1234", "hunter2", 12, job_index).go()``

In this example the request ID is 12.
