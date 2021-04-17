from pathlib import Path
import asyncio
from concurrent.futures import ThreadPoolExecutor
import functools
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
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
]


def fetch_one(session, project, timeout=3, headers=None):
    url = (
        f'https://api.github.com/repos/{project["account"]}/'
        f'{project["project"]}/releases/latest'
    )
    with session.get(url, timeout=timeout, headers=headers) as response:
        response.raise_for_status()
        data = response.json()
        project['latest_version'] = data['tag_name']
        # Find the first asset that's either .exe or .jar
        asset_we_want = next(
            item
            for item in data['assets']
            if item['name'].endswith(('.exe', '.jar', '.rar', '.zip'))
        )
        project['asset_download'] = asset_we_want['browser_download_url']
        project['asset_name'] = asset_we_want['name']
        return project


async def get_data_asynchronous(headers=None):
    with ThreadPoolExecutor(max_workers=10) as executor:
        with requests.Session() as session:
            retry_strategy = Retry(
                total=3,
                status_forcelist=[429, 500, 502, 503, 504],
                method_whitelist=["HEAD", "GET", "OPTIONS"]
            )
            adapter = HTTPAdapter(max_retries=retry_strategy)
            session.mount("https://", adapter)
            session.mount("http://", adapter)

            loop = asyncio.get_event_loop()
            tasks = [
                loop.run_in_executor(
                    executor,
                    functools.partial(
                        fetch_one,
                        session,
                        project,
                        headers=headers
                    )
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
                progress_trackers_complete = int(
                    num_progress_trackers * percent_done
                )
                done = '=' * progress_trackers_complete
                not_done = ' ' * (
                    num_progress_trackers - progress_trackers_complete
                )

                print(
                    f'[{done}{not_done}] {percent_done:.2%}',
                    end='\r',
                    flush=True
                )
        print()  # escape carridge escaped line
    return (time.perf_counter() - start)


def get_installed_versions():
    with open(downloaded_files_info) as f:
        apparent_downloaded = json.load(f)
    # for each file, check if it still exists
    # if it does, add the installed version to projects_we_want
    for project in apparent_downloaded:
        if Path(downloads_dir, project['asset_name']).exists():
            if remote_proj := next((
                    item
                    for item in projects_we_want
                    if item['id'] == project['id']
                ), None
            ):
                remote_proj['installed_ver'] = project['installed_ver']


if __name__ == '__main__':
    # Check if downloads folder exists. If not, make it.
    downloads_dir.mkdir(parents=True, exist_ok=True)

    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    if downloaded_files_info.exists():
        get_installed_versions()

    # Get current versions asynchronously
    loop = asyncio.get_event_loop()
    projects_we_want = loop.run_until_complete(
        get_data_asynchronous(headers={'Accept': 'application/json', 'Authorization': f'token '})
    )

    for project in projects_we_want:
        print(
            f'Latest version of {project["project"]} is '
            f'{project["latest_version"]}'
        )

        if project.get('installed_ver', None) == project["latest_version"]:
            print('Latest version already installed, skipping...')
        else:
            file_save_path = Path(downloads_dir, project['asset_name'])
            print(f'Downloading {project["asset_name"]}')
            time_elapsed = download_file(
                project['asset_download'],
                file_save_path
            )
            print(
                'Finished downloading. Time taken: '
                f'{round(time_elapsed, 2)}'
            )
            project['installed_ver'] = project["latest_version"]

        print()  # Seperation

        # Remove this so that it isn't included in local file causing confusion
        del project["latest_version"]

    with open(downloaded_files_info, 'w') as f:
        json.dump(projects_we_want, f, indent=4)
