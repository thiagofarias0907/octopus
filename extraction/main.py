import datetime as dt
import glob
import logging
import os

import requests
import yaml
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from yaml import CLoader

from extraction import OctopusPlanParser, DetailedOfferParser, PlanOffer, PlanOfferEntity, Database
from extraction.exceptions import InvalidContentException

# logs
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

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

# starting point
current_time = dt.datetime.now()



def get_page(url: str):
    response_get = requests.get(url=url, headers=headers)
    html = response_get.text
    if response_get.status_code != 200:
        raise InvalidContentException(url, html)
    return html


def clear_data_files():
    if not os.path.exists('../data'):
        os.mkdir("../data")

    for file_name in glob.glob("../data/*.pdf"):
        os.remove(file_name)


def create_entity(offer: PlanOffer) -> PlanOfferEntity:
    return PlanOfferEntity(
        extraction_datetime=current_time,
        name=offer.name,
        raw_material_cost=offer.raw_material_cost,
        commercial_cost=offer.commercial_cost,
        file_name_path=offer.create_file_path_name(),
        time_rate_type=offer.time_rate_type,
        user_type=offer.user_type,
    )


if __name__ == '__main__':
    logger.info("Starting Main Script")
    clear_data_files()

    logger.info("Parsing first page")
    page_content = get_page(config['base_url'] + config['first_page'])
    parser = OctopusPlanParser(page_content, config['first_page'])

    logger.info("Downloading files")
    parser._download_files()

    next_page = parser.get_next_page_button_url()

    logger.info("Opening Browser")
    driver = webdriver.Firefox()
    driver.get(config['base_url'] + next_page)

    logger.info("Parsing second page")
    parser = None
    try:
        plan_offers_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".sc-56k6h2-0.jrHhzT"))
        )
        parser = DetailedOfferParser(driver.page_source, next_page)
    finally:
        driver.quit()
    detailed_offers = parser.get_offers()
    plan_offer_entities = list(map(create_entity, detailed_offers))

    logger.info("Inserting results into database")
    Database(config).insert(plan_offer_entities)

    logger.info("The script has run completely!")

