# Miscellaneous Tools
This repo contains some misc scripts & tools that I use across devices.

I'm slowly improving & adding them all into this one place for ease of use.

## pip requirements
These files contain the pip requirements for all of the python scripts in this repo

[`requirements.txt`](requirements.txt) is a hand-crafted file of all top-level dependancies.

[`requirements_freeze.txt`](requirements_freeze.txt) is the output from `pip freeze`

## [POE tools downloader](download_poe_tools.py)
This script looks up the latest version of some tools I use while playing [Path of Exile](https://www.pathofexile.com/).

Running this script will create a `downloads` directory in the repo directory.

When this script is ran, it will check if the most up to date version is already present. If not, the script will download it.

## [GGPK dragger](ggpk_defragment.rb)
Credit: https://gist.github.com/Zoxc/2393192

Requirements: `gem install bindata`

Run this to reduce the size of POE's Content.ggpk file, which grows in size with each patch.

## [Copy start script](CopyStart.ps1)
This script opens a file selector window. The file selected is the copied to the current user's startup folder.

## [Shortcuts auto hot key script](shortcuts.ahk)
This script contains some misc hotkeys I like to use. See file contents for what they are
