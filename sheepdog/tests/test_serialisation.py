# Sheepdog
# Copyright 2013 Adam Greig
#
# Released under the MIT license. See LICENSE file for details.

from nose.tools import assert_equal, assert_true

from sheepdog import serialisation

class TestSerialisation:
    def test_serialises_functions(self):
        def myfunc(a, b):
            return a + b
        fs = serialisation.serialise_function(myfunc)
        assert_equal(type(fs), bytes)
        f = serialisation.deserialise_function(fs)
        assert_equal(f(1, 2), myfunc(1, 2))

    def test_serialises_functions_other_python(self):
        # Check it does the right thing for the Python we're not running.
        # Not strictly needed but it gets 100% test coverage!

        def myfunc(a, b):
            return a + b
        
        class FakeFunc:
            pass

        func = FakeFunc()

        if hasattr(myfunc, "__code__"):
            func.func_code = myfunc.__code__
        else:
            func.__code__ = myfunc.func_code

        fs = serialisation.serialise_function(func)
        assert_equal(type(fs), bytes)
        f = serialisation.deserialise_function(fs)
        assert_equal(f(1, 2), myfunc(1, 2))

    def test_serialises_functions_with_namespaces(self):
        def myfunc(a):
            return a + b
        fs = serialisation.serialise_function(myfunc)
        f = serialisation.deserialise_function(fs, {"b": 10})
        assert_equal(f(1), 11)

    def test_serialises_with_pickle(self):
        args = [1, "two", 3.0, 4j, b"five"]
        s = serialisation.serialise_pickle(args)
        assert_equal(type(s), bytes)
        ds = serialisation.deserialise_pickle(s)
        assert_equal(ds, args)

    def test_serialises_namespaces(self):
        def f(a):
            return a + b
        ns = {"b": 12, "f": f, "mystr": "helloworld"}
        nss = serialisation.serialise_namespace(ns)
        assert_equal(type(nss), bytes)
        dns = serialisation.deserialise_namespace(nss)
        assert_equal(dns['f'](1), 13)
        del dns['f']
        del ns['f']
        assert_equal(ns, dns)

    def test_serialises_lists_of_args(self):
        args = [1, "two", 3.0, 4j, b"five"]
        s = serialisation.serialise_args(args)
        assert_equal(type(s), list)
        assert_true(all(type(item) == bytes for item in s))
        ds = serialisation.deserialise_args(s)
        assert_equal(ds, args)
