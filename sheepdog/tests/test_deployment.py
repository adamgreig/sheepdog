# Sheepdog
# Copyright 2013, 2014 Adam Greig
#
# Released under the MIT license. See LICENSE file for details.

from nose.tools import assert_equal, assert_true

try:
    from unittest.mock import Mock, MagicMock, patch, mock_open
except ImportError:
    from mock import Mock, MagicMock, patch, mock_open

import sheepdog.deployment

class TestDeployment:

    @patch('sheepdog.deployment.paramiko.SSHClient')
    def test_processes_config(self, mock_ssh):
        config = "Host test\nHostName mytest\nUser tester\nPort 1234\n"
        m = mock_open()
        m.return_value.__iter__.return_value = config.splitlines()
        with patch('sheepdog.deployment.open', m, create=True):
            d = sheepdog.deployment.Deployer("test", 22, "user")
        assert_equal(d.host, "mytest")
        assert_equal(d.user, "tester")
        assert_equal(int(d.port), 1234)

    @patch('sheepdog.deployment.paramiko.ProxyCommand')
    @patch('sheepdog.deployment.paramiko.SSHClient')
    def test_processes_proxycommand(self, mock_ssh, mock_proxy):
        config = "Host test\nProxyCommand some command here\n"
        m = mock_open()
        m.return_value.__iter__.return_value = config.splitlines()
        with patch('sheepdog.deployment.open', m, create=True):
            d = sheepdog.deployment.Deployer("test", 22, "user")
        mock_proxy.assert_called_with("some command here")
        assert_equal(d.sock, mock_proxy.return_value)
        mock_ssh.return_value.connect.assert_called_with(
            "test", 22, "user", key_filename=None,
            sock=mock_proxy.return_value)

    @patch('sheepdog.deployment.paramiko')
    def test_jobfile_path(self, mock_paramiko):
        d = sheepdog.deployment.Deployer("test", 22, "user")
        request_id = 23
        directory = ".sheepdog/"
        path = d._get_jobfile_path(request_id, directory)
        assert_equal(path, ".sheepdog/sheepdog_023.py")

    @patch('sheepdog.deployment.paramiko.SSHClient')
    def test_connects(self, mock_ssh):
        d = sheepdog.deployment.Deployer("test", 22, "user")
        mock_ssh.return_value.connect.assert_called_with(
            "test", 22, "user", sock=None, key_filename=None)

    @patch('sheepdog.deployment.paramiko.SSHClient')
    def test_uses_keyfile(self, mock_ssh):
        d = sheepdog.deployment.Deployer("test", 22, "user", "keyfilepath")
        mock_ssh.return_value.connect.assert_called_with(
            "test", 22, "user", sock=None, key_filename="keyfilepath")

    @patch('sheepdog.deployment.paramiko.SSHClient')
    def test_deploys(self, mock_ssh):
        sftp_cm = MagicMock()
        sftp = mock_ssh.return_value.open_sftp.return_value
        sftp.open.return_value = sftp_cm
        d = sheepdog.deployment.Deployer("test", 22, "user")
        d.deploy("jobfile contents", 123, "/path/to/dir")
        mock_ssh.return_value.open_sftp.assert_called_with()
        sftp.mkdir.assert_called_with("/path/to/dir", mode=0o750)
        sftp.open.assert_called_with("/path/to/dir/sheepdog_123.py", 'w')
        sftp_cm.__enter__().write.assert_called_with("jobfile contents")

    @patch('sheepdog.deployment.paramiko.SSHClient')
    def test_ignores_mkdir_failure(self, mock_ssh):
        sftp_cm = MagicMock()
        sftp = mock_ssh.return_value.open_sftp.return_value
        sftp.open.return_value = sftp_cm
        sftp.mkdir.side_effect = OSError()
        d = sheepdog.deployment.Deployer("test", 22, "user")
        d.deploy("jobfile contents", 123, "/path/to/dir")
        mock_ssh.return_value.open_sftp.assert_called_with()
        sftp.mkdir.assert_called_with("/path/to/dir", mode=0o750)
        sftp.open.assert_called_with("/path/to/dir/sheepdog_123.py", 'w')
        sftp_cm.__enter__().write.assert_called_with("jobfile contents")

    @patch('sheepdog.deployment.paramiko.SSHClient')
    def test_submits(self, mock_ssh):
        mock_ssh.return_value.exec_command.return_value = (Mock(),)*3
        d = sheepdog.deployment.Deployer("test", 22, "user")
        d.submit(123, "/path/to/dir")
        mock_ssh.return_value.exec_command.assert_called_with(
            "qsub /path/to/dir/sheepdog_123.py")
