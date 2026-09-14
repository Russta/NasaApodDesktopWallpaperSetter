import requests
import json
import os
import time
from PIL import Image
import socket

API_APOD_COUNT = 25

def _fetch_json(url, attempts=4, delay=5):
    last_issue = None
    for attempt in range(1, attempts + 1):
        try:
            r = requests.get(url, timeout=30)
            if r.status_code == 200 and r.text.strip():
                return r.json()
            last_issue = f"HTTP {r.status_code}, body length {len(r.text)}"
        except Exception as e:
            last_issue = str(e)
        print(f"NASA API attempt {attempt}/{attempts} failed ({last_issue}); retrying in {delay}s...")
        time.sleep(delay)
    raise RuntimeError(f"NASA API gave no usable response after {attempts} attempts. Last issue: {last_issue}")

def get_data(api_key):
    return _fetch_json(f'https://api.nasa.gov/planetary/apod?api_key={api_key}')

def get_data_by_date(api_key, date):
    return _fetch_json(f'https://api.nasa.gov/planetary/apod?api_key={api_key}&date={date}')

def get_data_array(api_key):
    return _fetch_json(f'https://api.nasa.gov/planetary/apod?api_key={api_key}&count={API_APOD_COUNT}')

def get_date(response):
    return response['date']

def get_explaination(response):
    return response['explanation']

def get_hdurl(response):
    return response['hdurl']

def get_media_type(response):
    return response['media_type']

def get_service_version(response):
    return response['service_version']

def get_title(response):
    return response['title']

def get_url(response):
    return response['url']

def get_thumbnail_url(response):
    return response['thumbnail_url']

def download_image(url, date):
    apod_dir_path = getProperDirectoryPath()
    complete_file_path = os.path.join(apod_dir_path, f'{date}.png')
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0",
        "Accept-Encoding": "*",
        "Connection": "keep-alive"
    }
    if os.path.isfile(complete_file_path) == False:
        raw_image = requests.get(url, headers=headers).content
        with open(complete_file_path, 'wb') as file:
            file.write(raw_image)
    return complete_file_path

def getProperDirectoryPath():
    base_path = os.path.expanduser("~\\Pictures\\")
    directory = "NasaApod"
    apod_dir_path = os.path.join(base_path, directory)
    if not os.path.isdir(apod_dir_path):
        os.makedirs(apod_dir_path)
    return os.path.abspath(apod_dir_path)

def convert_image(image_path):
    path_to_image = os.path.normpath(image_path)
    basename = os.path.basename(path_to_image)
    filename_no_extension = basename.split(".")[0]
    base_directory = os.path.dirname(path_to_image)
    image = Image.open(path_to_image)
    image.save(f"{base_directory}/{filename_no_extension}.png")

def is_connected():
    try:
        socket.create_connection(("1.1.1.1", 53))
        return True
    except OSError:
        pass
    return False