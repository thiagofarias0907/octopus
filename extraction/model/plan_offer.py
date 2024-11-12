from pydantic import BaseModel
import os
import datetime as dt


class PlanOffer(BaseModel):
    """
    Model class to help handling the web scraping processes and functions
    """
    name: str = ""
    commercial_cost: float = 0.0
    file_url: str = ""

    time_rate_type: str = None
    raw_material: str = None
    user_type: str = None
    raw_material_cost: str = None

    def create_file_path_name(self):
        return f"{os.getcwd().replace('\\', '/').split("/extraction")[0]}/data/{self.name.lower().replace(' ', '_')}_{dt.date.today().isoformat()}.pdf"
