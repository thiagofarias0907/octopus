from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped

import datetime as dt
class Base(DeclarativeBase):
    pass

class PlanOfferEntity(Base):
    """
    Model class representing the database Entity in PostgreSQL using SQLAlchemy ORM mapping. I cloud have merged both
    models, using only one, but I wanted to avoid issues with the not null fields, which are different between both.
    """
    __tablename__ = "plan_offer"

    extraction_datetime: Mapped[dt.datetime] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(primary_key=True)
    raw_material_cost: Mapped[str] = mapped_column(primary_key=True)
    commercial_cost: Mapped[float] = mapped_column(primary_key=True)
    file_name_path: Mapped[str] = mapped_column(primary_key=True)
    time_rate_type: Mapped[str] = mapped_column(primary_key=True)
    user_type: Mapped[str] = mapped_column(primary_key=True)
    
    def __repr__(self) -> str:
        return f"PlanOffer(name={self.name!r}, time_rate_type={self.time_rate_type!r}, raw_material_cost={self.raw_material_cost!r}, commercial_cost={self.commercial_cost!r})"
