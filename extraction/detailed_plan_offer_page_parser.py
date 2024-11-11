import re
from typing import List

from bs4 import BeautifulSoup

from extraction.model import PlanOffer
from extraction.exceptions import InvalidContentException, ParsingFailureException


class DetailedOfferParser:
    """

    It seems that those class naming is server controlled, so it may be risky to use them as they can change frequently
    and this code will be broken in the future. On the other side, there's a json format data in the script tag,
    but some info are not the same as the rendered to the user, so I avoided using the json data.
    To access the structured data, one could simply use: self.__soup.select("script#__NEXT_DATA__")[0]
    """

    def __init__(self, html_content: str, url: str):
        if (html_content is None) or ("Seleziona la tariffa" not in html_content):
            raise InvalidContentException(content=html_content, url=url)

        self.__soup = BeautifulSoup(html_content, 'html.parser')
        self.__plan_offers: List[PlanOffer] = None
        self.__url = url

    def get_offers(self) -> List[PlanOffer]:
        if self.__plan_offers is not None:
            return self.__plan_offers

        offer_divs = self.__soup.select(".sc-zp1d3d-0.kJzAjt")
        if len(offer_divs) == 0:
            raise ParsingFailureException("class='sc-zp1d3d-0 kJzAjt'", self.__url)

        plan_offers = []
        for offer in offer_divs:
            try:
                plan_offer = PlanOffer()
                plan_offer.name = offer.select("h2")[0].text

                costs = offer.select(".sc-56k6h2-0.ihMmyR")[0].select('p')
                plan_offer.raw_material_cost = costs[0].text

                commercial_cost = float(re.findall("[\\d,.]+", costs[1].text)[0].replace(".", '').replace(",", "."))
                plan_offer.commercial_cost = commercial_cost

                additional_info = offer.select(".sc-1b2n8ps-0.bPclNy")[0].select('span')

                plan_offer.time_rate_type = additional_info[1].text.split(' ')[1].strip()
                plan_offer.user_type = additional_info[3].text.split(' ')[1].strip()

                plan_offers.append(plan_offer)
            except Exception as ex:
                raise ParsingFailureException(offer.text, ex.__str__())
        self.__plan_offers = plan_offers
        return plan_offers
