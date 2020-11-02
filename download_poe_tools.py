from string import Template
from pathlib import Path
import asyncio
from concurrent.futures import ThreadPoolExecutor
import functools
import requests
from requests.exceptions import ConnectionError, ReadTimeout
import time


dirname = Path(__file__).parent.absolute()

github_latest_tag_template = Template('https://github.com/$account/$project/releases/latest')
github_file_download_template = Template('https://github.com/$account/$project/releases/download/$version/$filename')

projects_we_want = [
    {'account': 'SnosMe', 'project': 'awakened-poe-trade', 'asset_template': Template('Awakened-PoE-Trade-Setup-$ver.exe')},
    {'account': 'PoE-Overlay-Community', 'project': 'PoE-Overlay-Community-Fork', 'asset_template': Template('poe-overlay.$ver.exe')},
    {'account': 'lemasato', 'project': 'POE-Trades-Companion', 'asset_template': Template('POE-Trades-Companion-AHK-v$ver.zip')},
    {'account': 'Exslims', 'project': 'MercuryTrade', 'asset_template': Template('MercuryTrade.jar'), 'no_version_in_asset_name': True},
    #{'account': 'viktorgullmark', 'project': 'exilence-next', 'asset_template': Template('Exilence-Next-Setup-$ver.exe')}
]

def get_set_event_loop():
    try:
        return asyncio.get_event_loop()
    except RuntimeError as e:
        if e.args[0].startswith('There is no current event loop'):
            asyncio.set_event_loop(asyncio.new_event_loop())
            return asyncio.get_event_loop()
        raise e

# Instance is a tuple of (<sub-domain>, <friendly_name>)
def fetch_one(session, project, timeout=3, retries=0, retry_limit=3, headers=None):
    url = github_latest_tag_template.substitute(
        account=project['account'], project=project['project']
    )
    try:
        with session.get(url, timeout=timeout, headers=headers) as response:
            response.raise_for_status()
            data = response.json()
            project['version'] = data['tag_name']
            return project
    except (ConnectionError, ReadTimeout) as e:
        if retries < retry_limit:
            return fetch_one(session, url, retries=retries+1)
        else:
            raise e

async def get_data_asynchronous(headers=None):
    with ThreadPoolExecutor(max_workers=10) as executor:
        with requests.Session() as session:
            loop = get_set_event_loop()
            tasks = [
                loop.run_in_executor(
                    executor,
                    functools.partial(fetch_one, session, project, headers=headers)
                )
                for project in projects_we_want
            ]
            return await asyncio.gather(*tasks)

def download_file(url, file_save_path):
    with open(file_save_path, 'wb') as f, requests.get(url, stream=True) as r:
        r.raise_for_status()

        start = time.perf_counter()
        total_length = int(r.headers.get('content-length'))
        num_progress_trackers = 50
        download_progress = 0

        for chunk in r.iter_content(chunk_size=16*1024):
            if chunk:  # filter out keep-alive new chunks
                download_progress += len(chunk)
                f.write(chunk)
                percent_done = download_progress / total_length
                progress_trackers_complete = int(num_progress_trackers * percent_done)
                print('[{done}{not_done}] {percent_done}%'.format(
                    done='=' * progress_trackers_complete,
                    not_done= ' ' * (num_progress_trackers-progress_trackers_complete),
                    percent_done=round(percent_done*100,2)
                ),end='\r',flush=True)
        print() # escape carridge escaped line
    return (time.perf_counter() - start) #time taken to download

if __name__ == '__main__':
    # Check if downloads folder exists. If not, make it.
    Path(dirname, 'downloads').mkdir(parents=True, exist_ok=True)

    # Get current versions asynchronously
    loop = get_set_event_loop()
    verion_numbers_future = asyncio.ensure_future(get_data_asynchronous(headers={'Accept': 'application/json'}))
    projects_we_want = loop.run_until_complete(verion_numbers_future)

    for project in projects_we_want:
        print(f'Latest version of {project["project"]} is {project["version"]}')
        
        # Remove v's as they aren't included in the asset name
        latest_version_without_v = project["version"][1:] if project["version"][0] =='v' else project["version"]

        # POE-Trades-Companion uses dashes in the asset name
        if project['project'] == 'POE-Trades-Companion': latest_version_without_v = latest_version_without_v.replace('.', '-')

        asset_name = project['asset_template'].substitute(ver=latest_version_without_v)
        asset_url = github_file_download_template.substitute(
            account=project['account'], project=project['project'],
            version=project["version"], filename=asset_name
        )

        # If the asset doesn't include a version in the name
        # insert the version at the end of the file name, before the file type
        if project.get('no_version_in_asset_name', False):
            asset_name_list = asset_name.split('.')
            asset_name_list.insert(len(asset_name_list) - 1, latest_version_without_v)
            asset_name = '.'.join(asset_name_list)

        file_save_path = Path(dirname, 'downloads', asset_name)
        if file_save_path.is_file():
            print(f'Found {asset_name} not downloading new.')
        else:
            print(f'Downloading {asset_name}')
            time_elapsed = download_file(asset_url, file_save_path)
            print(f'Finished downloading. Time taken: {round(time_elapsed, 2)}')
        print() # Seperation