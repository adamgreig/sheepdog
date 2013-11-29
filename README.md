# Sheepdog

Make Grid Engine a bit more useful from Python.

## Overview

Running large map style operations on a Grid Engine cluster can be frustrating.
Array jobs can only give scripts an input like some range() function call, but
this is rarely sufficient.  Collecting results is a huge pain.  Suddenly there
are text files everywhere and you feel an overwhelming sense of mediocracy.

Sheepdog aims to make life better for a somewhat specific use case:

1. You're using Python. Hopefully even Python 3.3. You're using numpy.

2. You've got access to a Grid Engine cluster on some remote machine.  It can
   also run Python, somehow or other.  The cluster computers and your client
   computer can all communicate over a network.

3. You have a function of several parameters and you want to run it many times
   with different arguments.  Results should come back nicely collated, and are
   reasonably small (you're not too worried if result objects get copied in
   memory).

4. You're a PhD student in Div F at CUED desperately trying to use *fear*
   effectively.

To accomplish these aims, Sheepdog:

1. Takes your function and N sets of arguments, serializes both
2. Creates a mapping range(N) to arguments
3. Starts a network interface, the eponymous dog
4. Starts a size N array job on the Grid Engine cluster, running sheep, the
   sheepdog client (of course)
5. Each sheep maps its array job ID into an actual set of arguments, and
   fetches the Python function to execute as well
6. The function is executed with the arguments
7. The result is sent back over the network
8. Results are collated against arguments

This is very similar to:

* Celery. Yes. Very similar.
* rq. Quite similar.
* Resque. But it's written in Python!
* Every other distributed map compute queue thing ever written.

## Usage

Coming Soon