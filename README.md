# Miscellaneous Tools
This repo contains some misc scripts & tools that I use across devices.

I'm slowly improving & adding them all into this one place for ease of use.

## [POE tools downloader](download_poe_tools.py)
This script looks up the latest version of some tools I use while playing [Path of Exile](https://www.pathofexile.com/).

Running this script will create a `downloads` directory in the repo directory.

When this script is ran, it will check if the most up to date version is already present. If not, the script will download it.

## pip requirements
[`requirements.txt`](requirements.txt) is a hand-crafted file of all top-level dependancies.

[`requirements_freeze.txt`](requirements_freeze.txt) is the output from `pip freeze`
