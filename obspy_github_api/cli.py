"""
Command line Interface for obspy_github_api
"""
import json
from typing import Optional

import typer

from obspy_github_api.obspy_github_api import make_ci_json_config

app = typer.Typer()

DEFAULT_CONFIG_PATH = "obspy_config/conf.json"


@app.command()
def make_config(
    issue_number: int, path: str = DEFAULT_CONFIG_PATH, token: Optional[str] = None
):
    """
    Create ObsPy's configuration json file for a particular issue.

    This command parses the comments in an issue's text looking for any magic
    strings (defined in ObsPy's issue template) and stores the values assigned
    to them to a json file for later use.

    The following names are stored in the config file:
        module_list - A string of requested modules separated by commas.
        module_list_spaces - A string of requested modules separated by spaces.
        docs - True if a doc build is requested.
    """
    make_ci_json_config(issue_number, path=path, token=token)


@app.command()
def read_config_value(name: str, path: str = DEFAULT_CONFIG_PATH):
    """
    Read a value from the configuration file.
    """
    with open(path, "r") as fi:
        params = json.load(fi)
    value = params[name]
    print(value)
    return value


def main():
    app()


if __name__ == "__main__":
    main()
