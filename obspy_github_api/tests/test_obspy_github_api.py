# -*- coding: utf-8 -*-
import mock

from obspy_github_api import (
    check_docs_build_requested,
    get_requested_modules,
    get_commit_status,
    get_commit_time,
    get_issue_numbers_that_request_docs_build,
    get_module_test_list,
    make_ci_json_config,
)


MOCK_DEFAULT_MODULES = ["core", "clients.arclink"]
MOCK_ALL_MODULES = MOCK_DEFAULT_MODULES + ["clients.fdsn", "geodetics"]


def test_check_docs_build_requested():
    assert check_docs_build_requested(100) is False
    assert check_docs_build_requested(101) is True
    assert check_docs_build_requested(101) is True


def test_check_specific_module_tests_requested():
    assert get_requested_modules(100) is False
    assert get_requested_modules(101) is True
    assert get_requested_modules(102) == [
        "clients.arclink",
        "clients.fdsn",
    ]


@mock.patch("obspy.core.util.base.DEFAULT_MODULES", MOCK_DEFAULT_MODULES)
@mock.patch("obspy.core.util.base.ALL_MODULES", MOCK_ALL_MODULES)
def test_get_module_test_list():
    assert get_module_test_list(100) == sorted(MOCK_DEFAULT_MODULES)
    assert get_module_test_list(101) == sorted(MOCK_ALL_MODULES)
    assert get_module_test_list(102) == sorted(
        set.union(set(MOCK_DEFAULT_MODULES), ["clients.arclink", "clients.fdsn"])
    )


def test_get_commit_status():
    # pr = 1507
    sha = "f74e0f5bcf26a47df6138c1ce026d9d14d68c4d7"
    assert get_commit_status(sha) == "pending"
    assert get_commit_status(sha, context="docker-testbot") == "pending"
    assert (
        get_commit_status(sha, context="continuous-integration/appveyor/branch")
        == "success"
    )
    assert (
        get_commit_status(sha, context="continuous-integration/appveyor/pr")
        == "success"
    )
    assert (
        get_commit_status(sha, context="continuous-integration/travis-ci/pr")
        == "success"
    )
    assert get_commit_status(sha, context="coverage/coveralls") == "failure"


def test_get_commit_time():
    sha = "f74e0f5bcf26a47df6138c1ce026d9d14d68c4d7"
    assert get_commit_time(sha) == 1471906365.0


def test_get_issue_numbers_that_request_docs_build():
    issues = get_issue_numbers_that_request_docs_build()
    assert isinstance(issues, list)
    for issue in issues:
        assert isinstance(issue, int)


class TestConfig:
    """Tests for creating the configuration file"""

    def test_json_ci_config(self):
        """Tests contents of configuration dict."""
        config_dict = make_ci_json_config(100, path=None)
        assert isinstance(config_dict, dict)
        # ensure module list elements don't end in '.'
        module_list_split = config_dict["module_list"].split(",")
        assert all([not x.endswith(".") for x in module_list_split])

    def test_no_ellipses(self):
        """Ensure the literal 'obspy....' is not in the module list. """
        config_dict = make_ci_json_config(2591, path=None)
        module_list = config_dict["module_list"]
        module_list_split = module_list.split(",")
        # There should never be more than one consecutive dot
        assert not any([".." in x for x in module_list_split])
