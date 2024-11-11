import re
from typing import List
import os

from concurrent.futures import ThreadPoolExecutor
import requests

from bs4 import BeautifulSoup

from extraction.model import PlanOffer
from extraction.exceptions import InvalidContentException, DownloadException, ParsingFailureException


class OctopusPlanParser:
    """"

    It seems that those class naming is server controlled, so it may be risky to use them as they can change frequently
    and this code will be broken in the future. On the other side, there's a json format data in the script tag,
    but some info are not the same as the rendered to the user, so I avoided using the json data.
    To access the structured data, one could simply use: self.__soup.select("script#__NEXT_DATA__")[0]
    """

    def __init__(self, html_content: str, url: str):
        if (html_content is None) or ("Le nostre tariffe luce" not in html_content):
            raise InvalidContentException(content=html_content, url=url)

        self.__soup = BeautifulSoup(html_content, 'html.parser')
        self.__plan_offers: List[PlanOffer] = None
        self.__url = url

    def get_offers(self) -> List[PlanOffer]:
        if self.__plan_offers is not None:
            return self.__plan_offers

        offer_divs = self.__soup.select(".sc-zp1d3d-0.jaoHRV")
        if len(offer_divs) == 0:
            raise ParsingFailureException("class='sc-zp1d3d-0 jaoHRV'", self.__url)

        plan_offers = []
        for offer in offer_divs:
            try:
                plan_offer = PlanOffer()
                plan_offer.name = offer.select("h2")[0].text

                cost_text = offer.select(".sc-56k6h2-0.kOMWpF > .sc-56k6h2-0.dCtzTe")[-1].select('p')[-1].text.strip()
                commercial_cost = float(re.findall("[\\d,.]+", cost_text)[0].replace(".", '').replace(",", "."))
                plan_offer.commercial_cost = commercial_cost

                plan_offer.file_url = offer.select(".sc-zp1d3d-0.klwkou > .sc-f752lt-0.dTsYAl")[0].get("href")

                plan_offers.append(plan_offer)
            except Exception as ex:
                raise ParsingFailureException(offer.text, ex.__str__())

        self.__plan_offers = plan_offers
        return plan_offers

    def get_next_page_button_url(self) -> str:
        next_url = None
        try:
            pseudo_button = self.__soup.select("a.sc-1bcn1h0-1.kOkVgW")[0]
            next_url = pseudo_button.get("href")
        except Exception as ex:
            raise ParsingFailureException("a.sc-1bcn1h0-1.kOkVgW", self.__url)
        return next_url

    def _download_files(self):
        with ThreadPoolExecutor() as executor:
            executor.map(self._download, self.get_offers())

    @staticmethod
    def _download(offer: PlanOffer):
        try:
            response = requests.get(offer.file_url)
            file_name = offer.create_file_path_name()
            if response.status_code != 200:
                raise DownloadException(file_name, response.status_code, offer.file_url)

            with open(file_name, mode="wb") as file:
                file.write(response.content)

            if os.path.getsize(file_name) == 0:
                raise DownloadException(offer.create_file_path_name(), "Empty File", offer.file_url)

        except Exception as ex:
            raise DownloadException(offer.create_file_path_name(), ex, offer.file_url)

    @staticmethod
    def should_download_all_pdfs(plan_offers) -> bool:
        for offer in plan_offers:
            if offer.commercial_cost < 100:
                return True
        return False
