
from extraction import OctopusParser
import requests
import os
import glob
import yaml
from yaml import CLoader

from extraction.exceptions import InvalidContentException

# Local Config File
config = None
with open(os.path.dirname(__file__) + '/local-config.yml', 'r', encoding='utf8') as file:
    config = yaml.load(file, Loader=CLoader)

# Headers
headers = {
    "host": "octopusenergy.it",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "accept-language": "it;q=0.8,en-US;q=0.5,en;q=0.3",
    # "accept-encoding": "gzip, deflate, br, zstd",
    "connection": "keep-alive"
}

def get_page(url:str):
    response_get =  requests.get(url=url, headers=headers)
    html = response_get.text
    if response_get.status_code != 200:
        raise InvalidContentException(url,html)
    return html

def clear_data_files():
    for file_name in glob.glob("../data/*.pdf"):
        os.remove(file_name)

if __name__ == '__main__':
    clear_data_files()

    page_content = get_page(config['base_url']+config['first_page'])
    parser = OctopusParser(page_content, config['first_page'])

    parser._download_files()

    next_page = parser.get_next_page_button_url()
    next_page_content = get_page(config['base_url']+next_page)
    parser = OctopusParser(next_page_content, next_page)

