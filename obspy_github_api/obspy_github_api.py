# -*- coding: utf-8 -*-
import datetime
import os
import re
import time
import warnings

import github3


# regex pattern in comments for requesting a docs build
PATTERN_DOCS_BUILD = r'\+DOCS'
# regex pattern in comments for requesting tests of specific submodules
PATTERN_TEST_MODULES = r'\+TESTS:([a-zA-Z0-9_\.,]*)'


try:
    # github API token with "repo.status" access right (if used to set commit
    # statuses) or with empty scope; to get around rate limitations
    token = os.environ["OBSPY_COMMIT_STATUS_TOKEN"]
except KeyError:
    msg = ("Could not get authorization token for ObsPy github API "
           "(env variable OBSPY_COMMIT_STATUS_TOKEN)")
    warnings.warn(msg)
    gh = github3.GitHub()
else:
    gh = github3.login(token=token)


def check_specific_module_tests_requested(issue_number):
    """
    Checks if tests of specific modules are requested for given issue number
    (e.g. by magic string '+TESTS:clients.fdsn,clients.arclink' or '+TESTS:ALL'
    anywhere in issue description or comments).
    Accumulates any occurrences of the above magic strings.

    :rtype: bool or list
    :returns: List of specific modules names to test in addition to default
        modules for given issue number or ``False`` if no specific tests are
        requested or ``True`` if all modules should be tested.
    """
    issue = gh.issue("obspy", "obspy", issue_number)
    modules_to_test = set()

    # process issue body/description
    match = re.search(PATTERN_TEST_MODULES, issue.body)
    if match:
        modules = match.group(1)
        if modules == "ALL":
            return True
        modules_to_test = set.union(modules_to_test, modules.split(","))

    # process issue comments
    for comment in issue.comments():
        match = re.search(PATTERN_TEST_MODULES, comment.body)
        if match:
            modules = match.group(1)
            if modules == "ALL":
                return True
            modules_to_test = set.union(modules_to_test, modules.split(","))

    modules_to_test = sorted(list(modules_to_test))

    if not len(modules_to_test):
        return False

    return modules_to_test


def get_module_test_list(issue_number):
    """
    Gets the list of modules that should be tested for the given issue number.
    This needs obspy to be installed, because DEFAULT_MODULES and ALL_MODULES
    is used.

    :rtype: list
    :returns: List of modules names to test for given issue number.
    """
    from obspy.core.util.base import DEFAULT_MODULES, ALL_MODULES

    modules_to_test = check_specific_module_tests_requested(issue_number)

    if modules_to_test is False:
        return DEFAULT_MODULES
    elif modules_to_test is True:
        return ALL_MODULES
    else:
        return sorted(list(set.union(set(DEFAULT_MODULES), modules_to_test)))


def check_docs_build_requested(issue_number):
    """
    Check if a docs build was requested for given issue number (by magic string
    '+DOCS' anywhere in issue comments).

    :rtype: bool
    """
    issue = gh.issue("obspy", "obspy", issue_number)
    if re.search(PATTERN_DOCS_BUILD, issue.body):
        return True
    for comment in issue.comments():
        if re.search(PATTERN_DOCS_BUILD, comment.body):
            return True
    return False


def get_pull_requests(state="open", sort="updated", direction="desc"):
    """
    Fetch a list of issue numbers for pull requests recently updated
    first, along with the PR data.
    """
    repo = gh.repository("obspy", "obspy")
    prs = repo.pull_requests(state=state, sort=sort, direction=direction)
    return prs


def get_commit_status(commit, context=None, fork='obspy'):
    """
    Return current commit status. Either for a specific context, or overall.

    :type commit: str
    :param commit: Commit SHA.
    :type context: str
    :param context: Commit status context (as a str) or ``None`` for overall
        commit status.
    :type fork: str
    :param fork: Obspy fork for commit (for commits on pull requests, 'obspy'
        should also work for commits on forks).
    :rtype: str or ``None``
    :returns: Current commit status (overall or for specific context) as a
        string or ``None`` if given context has no status.
    """
    # github3.py seems to lack support for fetching the "current" statuses for
    # all contexts.. (which is available in "combined status" for an SHA
    # through github API)
    repo = gh.repository(fork, "obspy")
    commit = repo.commit(commit)
    statuses = {}
    for status in commit.statuses():
        if (status.context not in statuses or
                status.updated_at > statuses[status.context].updated_at):
            statuses[status.context] = status

    # just return current status for given context
    if context:
        if context not in statuses:
            return None
        return statuses[context].state

    # return a combined status
    statuses = set(status.state for status in statuses.values())
    for status in ("pending", "error", "failure", "success"):
        if status in statuses:
            return status

    return None


def get_commit_time(commit, fork="obspy"):
    """
    :rtype: float
    :returns: Commit timestamp as POSIX timestamp.
    """
    repo = gh.repository(fork, "obspy")
    commit = repo.commit(commit)
    dt = datetime.datetime.strptime(commit.commit.committer["date"],
                                    '%Y-%m-%dT%H:%M:%SZ')
    return time.mktime(dt.timetuple())


def get_issue_numbers_that_request_docs_build(verbose=False):
    """
    :rtype: list of int
    """
    open_prs = get_pull_requests(state="open")

    if verbose:
        print("Checking the following open PRs if a docs build is requested "
              "and needed: {}".format(str(num for num, _ in open_prs)))

    todo = []
    for pr in open_prs:
        if check_docs_build_requested(pr.number):
            todo.append(pr.number)

    return todo


def set_pr_docs_that_need_docs_build(
        pr_docs_info_dir="/home/obspy/pull_request_docs", verbose=False):
    """
    Relies on a local directory with some files to mark when PR docs have been
    built etc.
    """
    prs_todo = get_issue_numbers_that_request_docs_build(verbose=verbose)

    for pr in prs_todo:
        number = pr.number
        fork = pr.head.user.login
        branch = pr.head.ref
        commit = pr.head.sha

        # need to figure out time of last push from commit details.. -_-
        time = get_commit_time(commit, fork)
        if verbose:
            print("PR #{} requests a docs build, latest commit {} at "
                  "{}.".format(number, commit,
                               str(datetime.fromtimestamp(time))))

        filename = os.path.join(pr_docs_info_dir, str(number))
        filename_todo = filename + ".todo"
        filename_done = filename + ".done"

        # create new stub file if it doesn't exist
        if not os.path.exists(filename):
            with open(filename, "wb") as fh:
                fh.write("{}\n{}\n".format(fork, branch).encode("UTF-8"))

        # update access/modify time of file
        os.utime(filename, (time, time))

        # check if nothing needs to be done..
        if os.path.exists(filename_done):
            time_done = os.stat(filename_done).st_atime
            if time_done > time:
                if verbose:
                    print("PR #{} was last built at {} and does not need a "
                          "new build.".format(
                              number, str(datetime.fromtimestamp(time_done))))
                continue
        # ..otherwise touch the .todo file
        with open(filename_todo, "wb"):
            if verbose:
                print("PR #{} build has been queued.".format(number))

    if verbose:
        print("Done checking which PRs require a docs build.")


def set_commit_status(commit, status, context, description,
                      target_url=None, fork="obspy", only_when_changed=True,
                      only_when_no_status_yet=False, verbose=False):
    """
    :param only_when_changed: Whether to only set a status if the commit status
        would change (commit statuses can not be updated or deleted and there
        is a limit of 1000 commit status per commit).
    :param only_when_no_status_yet: Whether to only set a status if the commit
        has no status with given context yet.
    """
    if status not in ("success", "pending", "error", "failure"):
        raise ValueError("Invalid status: {}".format(status))

    # check current status, only set a status if it would change the current
    # status..
    # (avoid e.g. flooding with "pending" status on continuously breaking docs
    #  builds that get started over and over again..)
    # if status would not change.. do nothing, don't send that same status
    # again
    if only_when_changed or only_when_no_status_yet:
        current_status = get_commit_status(commit, context)
        if only_when_no_status_yet:
            if current_status is not None:
                if verbose:
                    print("Commit {} already has a commit status ({}), "
                          "skipping.".format(commit, current_status))
                return
        if only_when_changed:
            if current_status == status:
                if verbose:
                    print("Commit {} status would not change ({}), "
                          "skipping.".format(commit, current_status))
                return

    repo = gh.repository(fork, "obspy")
    commit = repo.commit(commit)
    repo.create_status(sha=commit.sha, state=status, context=context,
                       description=description, target_url=target_url)
    if verbose:
        print("Set commit {} status (context '{}') to '{}'.".format(
            commit.sha, context, status))


def set_all_updated_pull_requests_docker_testbot_pending(verbose=False):
    """
    Set a status "pending" for all open PRs that have not been processed by
    docker buildbot yet.
    """
    open_prs = get_pull_requests(state="open")
    if verbose:
        print("Working on PRs: " + ", ".join(
            [str(pr.number) for pr in open_prs]))
    for pr in open_prs:
        set_commit_status(
            commit=pr.head.sha, status="pending", context="docker-testbot",
            description="docker testbot results not available yet",
            only_when_no_status_yet=True,
            verbose=verbose)


def get_docker_build_targets(
        context="docker-testbot", branches=["master", "maintenance_1.0.x"],
        prs=True):
    """
    Returns a list of build targets that need a build of a given context.

    Checks potential build targets, i.e. tips of open pull requests and tips of
    main branches (like "master"), whether they have a commit status of a given
    context or not.
    Returns a (space separated) string representation of the list of build
    targets as interpreted by the docker testing script in obspy/misc/docker
    (space separated list, individual build targets as `PRNUMBER_REPO:REF`,
    e.g.
    'XXX_obspy:master 1541_obspy:3edade31350b945620447a3b78f80c26782407ae').

    :type context: str
    :param context: Commit status context to check.
    :type branches: list
    :param branches: Branches to include as potential build targets.
    :type prs: bool
    :param prs: Whether to include open pull requests as potential build
        targets or not.
    :returns: String representation of list of build targets for use in docker
        testbot bash script (obspy/misc/docker).
    :rtype: string
    """
    if not branches and not prs:
        return ''

    status_needs_build = (None, 'pending')
    targets = []
    repo = gh.repository('obspy', 'obspy')

    if branches:
        for name in branches:
            branch = repo.branch(name)
            sha = branch.commit.sha
            status = get_commit_status(sha, context=context)
            if status not in status_needs_build:
                continue
            # branches don't have a PR number, use dummy placeholder 'XXX' so
            # that variable splitting in bash still works
            targets.append('XXX_obspy:{}'.format(sha))

    if prs:
        open_prs = get_pull_requests(state='open')
        for pr in open_prs:
            fork = pr.head.user
            sha = pr.head.sha
            status = get_commit_status(sha, context=context)
            if status not in status_needs_build:
                continue
            targets.append('{}_{}:{}'.format(str(pr.number), fork, sha))

    return ' '.join(targets)
