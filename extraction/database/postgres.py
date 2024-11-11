"""
CREATE TABLE public.plan_offer (
	extraction_datetime timestamp NOT NULL,
	name varchar NOT NULL,
	raw_material_cost varchar NOT NULL,
	commercial_cost float4 NOT NULL,
	file_name_path varchar NOT NULL,
	time_rate_type varchar NOT NULL,
	user_type varchar NOT NULL
);
CREATE INDEX plan_offer_extraction_datetime_idx ON public.plan_offer (extraction_datetime);

"""
from typing import List

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from extraction import PlanOfferEntity

class Database:

    def __init__(self, config):
        self.__engine = None
        self.__config = config['postgresql']

    def __get_engine(self):
        if self.__engine is not None:
            return self.__engine

        self.__engine = create_engine(
            f"postgresql+pg8000://{self.__config['user']}:{self.__config['pass']}@{self.__config['host']}:{self.__config['port']}/octopus",
            client_encoding='utf8', echo=True)
        return self.__engine

    def insert(self, plan_offers: List[PlanOfferEntity]):
        with Session(self.__get_engine()) as session:
            session.add_all(plan_offers)
            session.commit()
