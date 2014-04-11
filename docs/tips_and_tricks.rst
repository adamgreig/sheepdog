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
