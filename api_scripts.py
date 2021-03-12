import json
import time

import requests


key = ""
BASE_PATH = ""
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {key}"
}


def post_data(endpoint, data):
    url = f"{BASE_PATH}{endpoint}"

    start = time.perf_counter()
    resp = requests.post(url=url, json=data, headers=HEADERS)

    print(f"Time taken: {time.perf_counter()-start}s")

    try:
        return resp.json()
    except json.decoder.JSONDecodeError:
        return resp.text


def get_data(endpoint, params=None):
    url = f"{BASE_PATH}{endpoint}"

    start = time.perf_counter()
    resp = requests.get(url=url, params=params, headers=HEADERS)

    print(f"Time taken: {time.perf_counter()-start}s")

    try:
        return resp.json()
    except json.decoder.JSONDecodeError:
        return resp.text


def create_orgs():
    r = [
        post_data(
            "/organisations",
            {"name": f"Python test {i}"}
        )
        for i in range(5, 8)
    ]

    print(r)


def get_fields():
    response = get_data("/operative_field_schemas")

    for field in response:
        print(f"{field['slug']}: {field['name']}")


def get_sections():
    response = get_data("/operative_field_sections")

    for section in response:
        for field in section['fields']:
            print(f"{section['name']}: {field['slug']} - {field['name']}")


get_sections()
