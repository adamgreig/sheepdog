Sheepdog
========

Make Grid Engine a bit more useful from Python.

Overview
--------

Running large map style operations on a Grid Engine cluster can be
frustrating. Array jobs can only give scripts an input like some ``range()``
function call, but this is rarely sufficient. Collecting results is also
a huge pain. Suddenly there are shell scripts and result files
everywhere and you feel an overwhelming sense of mediocracy.

Sheepdog aims to make life better for a somewhat specific use case:

1. You're using Python. Hopefully even Python 3.3.

2. You've got access to a Grid Engine cluster on some remote machines.
   They can also run Python, somehow or other. The cluster computers and
   your client computer can all communicate over a network.

3. You have a function of several parameters and you want to run it many
   times with different arguments. Results should come back nicely
   collated, and are reasonably small (you're not too worried if
   argument or result objects get copied in memory).

4. You're a PhD student in Div F at CUED desperately trying to use
   *fear* effectively.

To accomplish these aims, Sheepdog:

1. Takes your function and N tuples of arguments, marshals both
2. Creates a mapping range(N) to arguments
3. Starts a network interface (over HTTP)
4. Starts a size N array job on the Grid Engine cluster, running the
   client
5. Each client talks to the server to map its array job ID into an
   actual set of arguments, and fetches the Python function to execute
   as well
6. The function is executed with the arguments
7. The result is sent back over the network
8. Results are collated against arguments

This is very similar to:

-  `pythongrid <https://code.google.com/p/pythongrid>`_. Almost
   identical. Sheepdog doesn't have to be run on the cluster head,
   though. And can't resubmit jobs or anything fancy like that. And
   isn't dead.
-  `gridmap <http://gridmap.readthedocs.org/>`_. A fork of pythongrid
   that is actually active and looks quite nice! Maybe look at gridmap.
-  `Celery <http://celeryproject.org/>`_. Yes. Pretty similar.
-  `rq <http://python-rq.org/>`_. Quite similar.
-  `Resque <http://resquework.org/>`_. But Resque is written in Ruby, boo.
-  Every other distributed map compute queue thing ever written.

Usage
-----

Ensure the GridEngine workers have Python available (you can specify
where the interpreter is) and that it has the requests module installed.

Then,

.. code:: python

        import sheepdog

        def f(a, b):
            return a + b

        args = [(1, 1), (1, 2), (2, 2)]
        config = {"host": "fear"}

        results = sheepdog.map_sync(f, args, config)
        print("\nReceived results:\n", results)
        # Received results:
        # [2, 3, 4]

Documentation
-------------

For docs, see `http://sheepdog.readthedocs.org/`_.
