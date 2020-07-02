"""
Tests for command line interface.
"""
import json
import tempfile
from pathlib import Path
from subprocess import run

import pytest


class TestCli:
    """"
    Test case for command line interface.
    """

    config_dir = tempfile.mkdtemp()
    config_path = Path(config_dir) / "conf.json"
    pr_number = 100

    @pytest.fixture(scope="class")
    def config_path(self, tmpdir_factory):
        tmpdir = tmpdir_factory.mktemp("obspy_config")
        return Path(tmpdir) / "conf.json"

    @pytest.fixture(scope="class")
    def populated_config(self, config_path):
        """ Get the config for the test PR. """
        run_str = f"obshub make-config {self.pr_number} --path {config_path}"
        run(run_str, shell=True, check=True)
        return config_path

    def test_path_exists(self, populated_config):
        """The config file should now exist."""
        assert Path(populated_config).exists()

    def test_is_json(self, populated_config):
        """Ensue the file created can be read by json module. """
        with Path(populated_config).open("r") as fi:
            out = json.load(fi)
        assert isinstance(out, dict)

    def test_read_config_value(self, populated_config):
        """Ensure the config value is printed to screen"""
        run_str = f"obshub read-config-value docs --path {populated_config}"
        out = run(run_str, shell=True, capture_output=True)
        assert out.stdout.decode("utf8").rstrip() == "False"
