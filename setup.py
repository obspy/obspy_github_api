"""
Setup for ObsPy's github api package.

Typically this is just used in CI pipelines.
"""
import inspect
import os
import re
import sys
from setuptools import setup

if sys.version_info < (2, 7):
    sys.exit('Python < 2.7 is not supported')

INSTALL_REQUIRES = [
    'github3.py>=1.0.0a1',  # works with 1.0.0a4
    # soft dependency on ObsPy itself, for function `get_module_test_list`
    # or the path to obspy.core.utils.base.py can be provided to avoid
    # needing to have ObsPy installed.
    ]

SETUP_DIRECTORY = os.path.dirname(os.path.abspath(inspect.getfile(
    inspect.currentframe())))


# get the package version from from the main __init__ file.
version_regex_pattern = r"__version__ += +(['\"])([^\1]+)\1"
for line in open(os.path.join(SETUP_DIRECTORY, 'obspy_github_api',
                              '__init__.py')):
    if '__version__' in line:
        version = re.match(version_regex_pattern, line).group(2)


def find_packages():
    """
    Simple function to find all modules under the current folder.
    """
    modules = []
    for dirpath, _, filenames in os.walk(
            os.path.join(SETUP_DIRECTORY, "obspy_github_api")):
        if "__init__.py" in filenames:
            modules.append(os.path.relpath(dirpath, SETUP_DIRECTORY))
    return [_i.replace(os.sep, ".") for _i in modules]


setup(
    name="obspy_github_api",
    version=version,
    description="Helper routines to interact with obspy/obspy via GitHub API",
    author="Tobias Megies",
    author_email="megies@geophysik.uni-muenchen.de",
    url="https://github.com/obspy/obspy_github_api",
    download_url="https://github.com/obspy/obspy_github_api.git",
    install_requires=INSTALL_REQUIRES,
    python_requires='>3.5',
    keywords=["obspy", "github"],
    packages=find_packages(),
    entry_points={},
    classifiers=[
        "Programming Language :: Python",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
    long_description="Helper routines to interact with obspy/obspy via GitHub "
                     "API",
    )
