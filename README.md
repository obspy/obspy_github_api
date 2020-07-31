# obspy_github_api
Helper routines to interact with obspy/obspy via GitHub API

## Quick start

The easiest way to use obspy_github_api is via its command line interface.

```shell script
# Use the magic strings found in issue 101's comments to create a config file
obshub make_config 101 --path obspy_config.json

# Read a specified option.
obshub read-config-value module_list --path obspy_config.json

# Use a value in the config in another command line utility.
export BUILDDOCS=`obshub read-config-value module_list --path obspy_config.json`
some-other-command --docs $BUILDDOCS
```

## Release Versions

Release versions are done from separate branches, see https://github.com/obspy/obspy_github_api/branches.

Release versions can be installed from: https://github.com/obspy/obspy_github_api/releases
