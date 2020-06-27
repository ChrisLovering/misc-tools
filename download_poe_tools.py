from string import Template
import requests
import time
import os
import pathlib

github_latest_tag_template = Template('https://github.com/$account/$project/releases/latest')
github_file_download_template = Template('https://github.com/$account/$project/releases/download/$version/$filename')
headers = {'Accept': 'application/json'}

dirname = os.path.dirname(os.path.abspath(__file__))

projects_we_want = [
    {'account': 'PathOfBuildingCommunity', 'project': 'PathOfBuilding', 'asset_template': Template('PathOfBuildingCommunity-Setup-$ver.exe')},
    {'account': 'PoE-Overlay-Community', 'project': 'PoE-Overlay-Community-Fork', 'asset_template': Template('poe-overlay-$ver.exe')},
    {'account': 'lemasato', 'project': 'POE-Trades-Companion', 'asset_template': Template('POE-Trades-Companion.exe')}
]

def get_latest_tag(url):
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    return r.json()['tag_name']

def get_version_number(project):
    latest_version = get_latest_tag(github_latest_tag_template.substitute(
        account=project['account'],
        project=project['project']
    ))
    return latest_version

def download_file(project, filename, version):
    url = github_file_download_template.substitute(
        account=project['account'], project=project['project'],
        version=version, filename=filename
    )
    filepath = os.path.join(dirname, 'downloads', filename)
    with open(filepath, 'wb') as f:
        start = time.perf_counter()
        r = requests.get(url, stream=True)
        total_length = int(r.headers.get('content-length'))
        dl = 0
        for chunk in r.iter_content(chunk_size=16*1024):
            dl += len(chunk)
            f.write(chunk)
            done = int(50 * dl / total_length)
            print("\r[%s%s] %s bps" % ('=' * done, ' ' * (50-done), dl//(time.perf_counter() - start)),end='',flush=True)
        print()
    return (time.perf_counter() - start)

if __name__ == '__main__':
    pathlib.Path(os.path.join(dirname, 'downloads')).mkdir(parents=True, exist_ok=True)
    for project in projects_we_want:
        print('Getting latest version of', project['project'], '...', end='', flush=True)
        latest_version = get_version_number(project)
        print(' Found version', latest_version)

        # Some people tag their github versions with a v, but don't include these v's in the file names...
        latest_version_without_v = latest_version[1:] if latest_version[0] =='v' else latest_version

        asset_name = project['asset_template'].substitute(ver=latest_version_without_v)
        print('Downloading', asset_name)
        time_elapsed = download_file(project, asset_name, latest_version)
        print('Finished downloading.', 'Time taken:', round(time_elapsed, 2))
        print()
