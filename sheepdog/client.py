# Sheepdog
# Copyright 2013 Adam Greig
#
# Released under the MIT license. See LICENSE file for details.

"""
Sheepdog's clientside code.

This code is typically only run on the worker, and this file is currently
only used by pasting it into a job file (as workers don't generally have
sheepdog itself installed).
"""

import time
import json
import base64
import traceback

try:
    from urllib.error import URLError
    from urllib.parse import urlencode
    from urllib.request import urlopen, Request
except ImportError:
    from urllib import urlencode
    from urllib2 import urlopen, Request, URLError

try:
    deserialise_function
except NameError:
    from sheepdog.serialisation import (deserialise_function,
                                        deserialise_arg,
                                        deserialise_namespace,
                                        serialise_pickle)

class Client:
    """Find out what to do, do it, report back."""
    HTTP_RETRIES = 10

    def __init__(self, url, password, request_id, job_index):
        self.url = url
        self.password = password
        self.request_id = request_id
        self.job_index = job_index

        userpass = ("sheepdog:" + self.password).encode()
        authstr = "Basic " + base64.b64encode(userpass).decode()
        self.authhdr = {"Authorization": authstr}

    def get_details(self):
        """Retrieve the function to run and arguments to run with from the
           server.
        """
        url = self.url + "?request_id={0}&job_index={1}"
        url = url.format(self.request_id, self.job_index)
        print("Fetching URL: {}".format(url))
        req = Request(url, headers=self.authhdr)
        tries = 0
        while tries < self.HTTP_RETRIES:
            try:
                response = urlopen(req)
                break
            except URLError:
                tries += 1
                time.sleep(1)
                continue
        if tries == self.HTTP_RETRIES:
            raise RuntimeError("Could not connect to server.")
       
        result = json.loads(response.read().decode())
        self.args = deserialise_arg(result['args'])
        self.ns = deserialise_namespace(result['ns'])
        self.func = deserialise_function(result['func'], self.ns)

    def run(self):
        """Run the downloaded function, storing the result."""
        if not hasattr(self, 'func') or not hasattr(self, 'args'):
            raise RuntimeError("Must call `get_details` before `run`.")
        try:
            self.result = self.func(*self.args)
            print(self.result)
        except:
            self._submit_error(traceback.format_exc())

    def submit_results(self):
        if not hasattr(self, 'result'):
            raise RuntimeError("Must call `run` before `submit_results`.")
        result = serialise_pickle(self.result)
        self._submit(self.url, dict(result=result))

    def _submit_error(self, error):
        self._submit(self.url + "error", dict(error=str(error)))

    def _submit(self, url, data):
        data.update(
            {"request_id": self.request_id, "job_index": self.job_index})
        encoded_data = urlencode(data).encode()
        req = Request(url, data=encoded_data, headers=self.authhdr)
        tries = 0
        while tries < self.HTTP_RETRIES:
            try:
                response = urlopen(req)
                break
            except URLError:
                tries += 1
                time.sleep(1)
                continue
        if tries == self.HTTP_RETRIES:
            raise RuntimeError("Could not submit to server.")

    def go(self):
        """Call get_details(), run(), submit_results().
           Just for convenience.
        """
        self.get_details()
        self.run()
        if hasattr(self, 'result'):
            self.submit_results()
