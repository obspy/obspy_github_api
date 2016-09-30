import inspect
import os
from setuptools import setup

INSTALL_REQUIRES = [
    'github3.py>=1.0.0a1',  # works with 1.0.0a4
    ]

SETUP_DIRECTORY = os.path.dirname(os.path.abspath(inspect.getfile(
    inspect.currentframe())))


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
    version="0.2.0",
    description="Helper routines to interact with obspy/obspy via GitHub API",
    author="Tobias Megies",
    author_email="megies@geophysik.uni-muenchen.de",
    url="https://github.com/obspy/obspy_github_api",
    download_url="https://github.com/obspy/obspy_github_api.git",
    install_requires=INSTALL_REQUIRES,
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
