"""
Sheepdog
Copyright 2013 Adam Greig

Clientside code.
"""

import json
import types
import base64
import marshal
import requests

class Client:
    """Find out what to do, do it, report back."""
    HTTP_RETRIES = 10

    def __init__(self, url, request_id, job_index):
        self.url = url
        self.request_id = request_id
        self.job_index = job_index

    def get_details(self):
        """Retrieve the function to run and arguments to run with from the
           server.
        """
        url = self.url + "?request_id={0}&job_index={1}"
        url = url.format(self.request_id, self.job_index)
        tries = 0
        while tries < self.HTTP_RETRIES:
            try:
                r = requests.get(url)
                break
            except (requests.ConnectionError, requests.Timeout):
                tries += 1
                continue
        if tries == self.HTTP_RETRIES:
            raise RuntimeError("Could not connect to server.")
       
        r = r.json()
        func_bin = base64.b64decode(r['func'])
        args_bin = base64.b64decode(r['args'])
        code = marshal.loads(func_bin)
        self.func = types.FunctionType(code, globals(), "f")
        self.args = marshal.loads(args_bin)

    def run(self):
        """Run the downloaded function, storing the result."""
        if not hasattr(self, 'func') or not hasattr(self, 'args'):
            raise RuntimeError("Must call `get_details` before `run`.")
        self.result = self.func(*self.args)

    def submit_results(self):
        if not hasattr(self, 'result'):
            raise RuntimeError("Must call `run` before `submit_results`.")
        result = base64.b64encode(marshal.dumps(self.result))
        tries = 0
        while tries < self.HTTP_RETRIES:
            try:
                r = requests.post(self.url,
                                  data=dict(request_id=self.request_id,
                                            job_index=self.job_index,
                                            result = result))
                break
            except (requests.ConnectionError, requests.Timeout):
                tries += 1
                continue
        if tries == self.HTTP_RETRIES:
            raise RuntimeError("Could not submit results to server.")

    def go(self):
        """Call get_details(), run(), submit_results().
           Just for convenience.
        """
        self.get_details()
        self.run()
        self.submit_results()
