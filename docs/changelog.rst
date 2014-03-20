Changelog
=========

Version 0.1
-----------

0.1.4
^^^^^
Released on 2014-03-20.

* Improve test coverage
* Refactor all default values to sheepdog/__init__.py
* Improved defaults:
    * Use ~/.sheepdog as the default working directory on the remote host
    * Use /usr/bin/python instead of /usr/bin/env python as this confuses GE
    * Quote user-provided shells in case they contain a space

0.1.3
^^^^^
Released on 2014-01-21.

* Change package layout to remove subpackages, because flat is better.
* Improve docstrings.
* Refactor serialisation to its own module which is used throughout Sheepdog.
* Store job files in ~/.sheepdog on remote server

0.1.2
^^^^^
Released on 2013-12-05.

* Adds the Requests package to requirements as you can't actually run the local
  code without it.

0.1.1
^^^^^
Released on 2013-12-04.

* Adds Python 2.7 compatibility by frobbing some bytes() in the sqlite stuff.

0.1.0
^^^^^
Released on 2013-12-04. First release.

* Contains :py:func:`sheepdog.map_sync`, the first top level
  utility function, plus the basic underlying sqlite storage and tornado/flask
  web server bits.
