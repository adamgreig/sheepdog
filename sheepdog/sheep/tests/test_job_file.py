"""
Sheepdog
Copyright 2013 Adam Greig

Job file testing code.
"""

from sheepdog.sheep import job_file

class TestJobFile:
    def test_includes_client(self):
        assert "Clientside code." in job_file.job_file("", 0, 0, 1)

    def test_ge_opts(self):
        assert "#$ -r y" in job_file.job_file("", 0, 0, 1, ["-r y"])

    def test_shebang(self):
        assert "#!/my/py" in job_file.job_file("", 0, 0, 1, [], "/my/py")

    def test_client_details(self):
        assert "Client(\"myurl\", 0, 1)" in job_file.job_file("myurl", 0, 1, 1)

    def test_array_job(self):
        assert "#$ -t 1-1000" in job_file.job_file("", 0, 1, 1000)
