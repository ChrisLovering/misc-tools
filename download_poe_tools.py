from pathlib import Path
import asyncio
from concurrent.futures import ThreadPoolExecutor
import functools
import requests
from requests.exceptions import ConnectionError, ReadTimeout
import time
import json


script_dirname = Path(__file__).parent.absolute()
downloads_dir = Path(script_dirname, 'downloads')
downloaded_files_info = Path(downloads_dir, 'downloaded.json')

projects_we_want = [
    {'id': 1, 'account': 'SnosMe', 'project': 'awakened-poe-trade'},
    {'id': 2, 'account': 'PoE-Overlay-Community', 'project': 'PoE-Overlay-Community-Fork'},
    {'id': 3, 'account': 'lemasato', 'project': 'POE-Trades-Companion'},
    {'id': 4, 'account': 'Exslims', 'project': 'MercuryTrade'},
    {'id': 5, 'account': 'viktorgullmark', 'project': 'exilence-next'},
]

def get_set_event_loop():
    try:
        return asyncio.get_event_loop()
    except RuntimeError as e:
        if e.args[0].startswith('There is no current event loop'):
            asyncio.set_event_loop(asyncio.new_event_loop())
            return asyncio.get_event_loop()
        raise e

def fetch_one(session, project, timeout=3, retries=0, retry_limit=3, headers=None):
    url = f'https://api.github.com/repos/{project["account"]}/{project["project"]}/releases/latest'
    try:
        with session.get(url, timeout=timeout, headers=headers) as response:
            response.raise_for_status()
            data = response.json()
            project['version'] = data['tag_name']
            # Find the first asset that's either .exe or .jar
            asset_we_want = next(item for item in data['assets'] if item['name'].endswith(('.exe', '.jar')))
            project['asset_download'] = asset_we_want['browser_download_url']
            project['asset_name'] = asset_we_want['name']
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
                done = '=' * progress_trackers_complete
                not_done =  ' ' * (num_progress_trackers-progress_trackers_complete)
                
                print(f'[{done}{not_done}] {percent_done:.2%}',end='\r',flush=True)
        print() # escape carridge escaped line
    return (time.perf_counter() - start) #time taken to download

def get_installed_versions():
    with open(downloaded_files_info) as f:
        apparent_downloaded = json.load(f)
    actual_downloaded = []
    for project in apparent_downloaded:
        if Path(downloads_dir, project['asset_name']).exists():
            actual_downloaded.append(project)
    return actual_downloaded


if __name__ == '__main__':
    # Check if downloads folder exists. If not, make it.
    downloads_dir.mkdir(parents=True, exist_ok=True)

    if downloaded_files_info.exists():
        installed_projects = get_installed_versions()
    else:
        installed_projects = None

    # Get current versions asynchronously
    loop = get_set_event_loop()
    verion_numbers_future = asyncio.ensure_future(get_data_asynchronous(
        headers={'Accept': 'application/json'}
    ))
    projects_we_want = loop.run_until_complete(verion_numbers_future)

    for project in projects_we_want:
        print(f'Latest version of {project["project"]} is {project["version"]}')

        if installed_projects:
            installed_ver = next((item for item in installed_projects if item["id"] == project['id']), None)
            if installed_ver and installed_ver['version'] == project["version"]:
                print(f'Latest version already installed, skipping...')
                print() # Seperation
                continue
            elif installed_ver:
                print(f'Found old version ({installed_ver}). ', end='', flush=True)

        file_save_path = Path(downloads_dir, project['asset_name'])
        print(f'Downloading {project["asset_name"]}')
        time_elapsed = download_file(project['asset_download'], file_save_path)
        print(f'Finished downloading. Time taken: {round(time_elapsed, 2)}')
        print() # Seperation
    
    with open(downloaded_files_info, 'w') as f:
        json.dump(projects_we_want, f, indent=4)