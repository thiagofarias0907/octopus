import re
from typing import List
import os

from concurrent.futures import ThreadPoolExecutor
import requests

from bs4 import BeautifulSoup

from extraction.model import PlanOffer
from extraction.exceptions import InvalidContentException, DownloadException, ParsingFailureException


class OctopusPlanParser:
    """
    First page webscraping code. It expects the html content and can return all the plan offers, get the next page url
    and download all files. The <$100 rule control must be done by the main script.

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
        """
        Extract the data for each plan offer and return them
        :return: List[PlanOffer]
        """
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
        """
        Extract the href value from the call-to-action button
        :return: url
        """
        next_url = None
        try:
            pseudo_button = self.__soup.select("a.sc-1bcn1h0-1.kOkVgW")[0]
            next_url = pseudo_button.get("href")
        except Exception as ex:
            raise ParsingFailureException("a.sc-1bcn1h0-1.kOkVgW", self.__url)
        return next_url

    def download_files(self):
        """
        Download all the CTE pdf files from the page's plan offers
        :return: None
        """
        with ThreadPoolExecutor() as executor:
            executor.map(self._download, self.get_offers())

    @staticmethod
    def _download(offer: PlanOffer):
        """Download a single file for the given PlanOffer's file url"""
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
        """
        It returns True if there is at least one plan offer below $100; False, if all are equal or greater than $100.
        Obs.: I understood that I should download all pdf if there was at least one plan offer lower than $100.
        I wasn't sure if I should download only the pdf for those with offers below 100."""
        for offer in plan_offers:
            if offer.commercial_cost < 100:
                return True
        return False
