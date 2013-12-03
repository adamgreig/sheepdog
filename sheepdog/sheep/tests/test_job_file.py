"""
Sheepdog
Copyright 2013 Adam Greig

Job file testing code.
"""

from sheepdog.sheep import job_file

class TestJobFile:
    def test_includes_client(self):
        assert "Clientside code." in job_file.job_file("", 0, 0)

    def test_ge_opts(self):
        assert "#$ -l ubuntu=1" in job_file.job_file("", 0, 0, ["-l ubuntu=1"])

    def test_shebang(self):
        assert "#!/my/python" in job_file.job_file("", 0, 0, [], "/my/python")

    def test_client_details(self):
        assert "Client(myurl, 0, 1)" in job_file.job_file("myurl", 0, 1)
