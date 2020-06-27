from string import Template
from pathlib import Path
import requests
import time

dirname = Path(__file__).parent.absolute()

github_latest_tag_template = Template('https://github.com/$account/$project/releases/latest')
github_file_download_template = Template('https://github.com/$account/$project/releases/download/$version/$filename')

projects_we_want = [
    {'account': 'PathOfBuildingCommunity', 'project': 'PathOfBuilding', 'asset_template': Template('PathOfBuildingCommunity-Setup-$ver.exe')},
    {'account': 'PoE-Overlay-Community', 'project': 'PoE-Overlay-Community-Fork', 'asset_template': Template('poe-overlay-$ver.exe')},
    {'account': 'lemasato', 'project': 'POE-Trades-Companion', 'asset_template': Template('POE-Trades-Companion-AHK-v$ver.zip')},
    {'account': 'Exslims', 'project': 'MercuryTrade', 'asset_template': Template('MercuryTrade.jar'), 'no_version_in_asset_name': True},
    {'account': 'viktorgullmark', 'project': 'exilence-next', 'asset_template': Template('Exilence-Next-Setup-$ver.exe')}
]

def get_version_number(project):
    url = github_latest_tag_template.substitute(
        account=project['account'], project=project['project']
    )
    r = requests.get(url, headers={'Accept': 'application/json'})
    r.raise_for_status()
    return r.json()['tag_name']

def download_file(url, file_save_path):
    with open(file_save_path, 'wb') as f, requests.get(url, stream=True) as r:
        # Used to calc elapsed time
        start = time.perf_counter()
        
        total_length = int(r.headers.get('content-length'))

        num_progress_trackers = 50
        download_progress = 0

        # This for loop is downloading a file and printing progress on a single line.
        for chunk in r.iter_content(chunk_size=16*1024):
            download_progress += len(chunk)
            f.write(chunk)
            percent_done = download_progress / total_length
            progress_trackers_complete = int(num_progress_trackers * percent_done)
            print('[{done}{not_done}] {percent_done}%'.format(
                done='=' * progress_trackers_complete,
                not_done= ' ' * (num_progress_trackers-progress_trackers_complete),
                percent_done=round(percent_done*100,2)
            ),end='\r',flush=True)

        # New line to escape carridge escaped line
        print()
    return (time.perf_counter() - start)

if __name__ == '__main__':
    # Check if downloads folder exists. If not, make it.
    Path(dirname, 'downloads').mkdir(parents=True, exist_ok=True)

    for project in projects_we_want:
        print('Getting latest version of', project['project'], '...', end='', flush=True)
        latest_version_tag = get_version_number(project)
        print(' Latest version is', latest_version_tag)
        
        # Some github latest tags start with a v's.
        # Need a var without these as they aren't included in the asset name
        latest_version_without_v = latest_version_tag[1:] if latest_version_tag[0] =='v' else latest_version_tag

        # POE-Trades-Companion uses dashes in the asset name
        if project['project'] == 'POE-Trades-Companion': latest_version_without_v = latest_version_without_v.replace('.', '-')

        # Build asset name based off version number
        asset_name = project['asset_template'].substitute(ver=latest_version_without_v)

        # Build the download url
        asset_url = github_file_download_template.substitute(
            account=project['account'], project=project['project'],
            version=latest_version_tag, filename=asset_name
        )

        # If the asset doesn't include a version in the name
        # insert the version at the end of the file name, before the file type
        if project.get('no_version_in_asset_name', False):
            asset_name_list = asset_name.split('.')
            asset_name_list.insert(len(asset_name_list) - 1, latest_version_without_v)
            asset_name = '.'.join(asset_name_list)

        # Check if file already exists before downloading
        file_save_path = Path(dirname, 'downloads', asset_name)
        if file_save_path.is_file():
            print("Found", asset_name, 'not downloading new.')
        else:
            print('Downloading', asset_name)
            time_elapsed = download_file(asset_url, file_save_path)
            print('Finished downloading. Time taken:', round(time_elapsed, 2))
        
        # New line is just for seperation
        print()
