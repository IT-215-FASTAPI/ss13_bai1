from sqlalchemy import Column, Integer, String, Float
from database import Base


class MenuItem(Base):
    __tablename__ = "menu_items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    dish_code = Column(String(50), unique=True, nullable=False, index=True)
    dish_name = Column(String(100), nullable=False)
    calorie_count = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    status = Column(String(30), default="AVAILABLE", nullable=False)
