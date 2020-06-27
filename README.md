# Common Tools
This repo contains common scripts & tools that I use accross devices.

## Path of Exile tools downloader python script
This script looks up the latest version of some tools I use while playing [Path of Exile](https://www.pathofexile.com/).

Running this script will create a `downloads` directory in the repo directory.

When this script is ran, it will check if the currently downloaded version is the most up to date version.

If it is, a new file will not be downloaded.

## pip Requirements
`requirements.txt` is a hand-crafted file of all top-level dependancies.

`requirements_freeze.txt` is the output from `pip freeze`