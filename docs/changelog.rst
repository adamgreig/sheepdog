Changelog
=========

Version 0.2
-----------

Starting to become stable and useful.

0.2.2
^^^^^
Released on 2014-10-27

* Fix a bug where multiple runs in the same Python session would break
* Count errors properly in verbose map mode
* Automatically call setrlimit when a mem_grab resource specifier is given

0.2.1
^^^^^
Released on 2014-07-10

* Documentation updates
* Remove redundant console output

0.2.0
^^^^^
Released on 2014-04-11

* Keep track of what servers are running to prevent duplicates being started
* Allow specification of pickle and marshal protocol versions
* Refactor __init__'s map_sync into map_async, get_results and map
  * *note that `map_sync` is now `map`*
* Handle task errors in the top level map and get_results functions
* Tidy examples somewhat

Version 0.1
-----------

Early work.

0.1.10
^^^^^^
Released on 2014-04-04.

* Port is now selected at random by default (instead of 7676)
* Removed fear-specific default `ge_opts`
* Swaped to Marshall protocol 2 so 3.4 doesn't get sad, but still using Pickle
  protocol 3 so Py3 hosts won't be able to talk to Py2 workers yet
* Added `ssh_keyfile` option so a specific passphraseless SSH key can be used
* Added HTTP Basic Auth to HTTP requests

0.1.9
^^^^^
Released on 2014-04-04.

* Documentation improvements
* Actually release to PyPi, which got skipped for 0.1.8

0.1.8
^^^^^
Released on 2014-03-21.

* Swap to Paramiko for SSH usage. Much nicer.
* Swap to urllib rather than Requests. A pity, but removes the dependency.
* Fix Tornado starting from inside IPython Notebook.
* Clients now print out their results so GridEngine can save it in the .o files

0.1.7
^^^^^
Released on 2014-03-21.

* Fix Py2 by using list() instead of list.copy()


0.1.6
^^^^^
Released on 2014-03-20.

* Fix tests for namespace serialisation.

0.1.5
^^^^^
Released on 2014-03-20.

* Fix bug where ge_opts would be appended to every map_sync call
* Fix bug where functions in the request namespace only got a copy
  of the namespace so global imports etc would not work

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
