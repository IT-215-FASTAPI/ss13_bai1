from typing import Optional
from pydantic import BaseModel, field_validator

ALLOWED_STATUS = {"AVAILABLE", "OUT_OF_STOCK"}


class MenuItemCreate(BaseModel):
    dish_code: str
    dish_name: str
    calorie_count: int
    price: float
    status: Optional[str] = "AVAILABLE"

    @field_validator("dish_code")
    @classmethod
    def validate_dish_code(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("dish_code không được để rỗng")
        return v

    @field_validator("dish_name")
    @classmethod
    def validate_dish_name(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("dish_name không được để rỗng")
        return v

    @field_validator("calorie_count")
    @classmethod
    def validate_calorie_count(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("calorie_count phải là số lớn hơn 0")
        return v

    @field_validator("price")
    @classmethod
    def validate_price(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("price phải là số lớn hơn 0")
        return v

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ALLOWED_STATUS:
            raise ValueError(f"status phải là một trong {ALLOWED_STATUS}")
        return v


class MenuItemUpdate(BaseModel):
    dish_code: Optional[str] = None
    dish_name: Optional[str] = None
    calorie_count: Optional[int] = None
    price: Optional[float] = None
    status: Optional[str] = None

    @field_validator("dish_code")
    @classmethod
    def validate_dish_code(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError("dish_code không được để rỗng")
        return v

    @field_validator("dish_name")
    @classmethod
    def validate_dish_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError("dish_name không được để rỗng")
        return v

    @field_validator("calorie_count")
    @classmethod
    def validate_calorie_count(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v <= 0:
            raise ValueError("calorie_count phải là số lớn hơn 0")
        return v

    @field_validator("price")
    @classmethod
    def validate_price(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and v <= 0:
            raise ValueError("price phải là số lớn hơn 0")
        return v

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ALLOWED_STATUS:
            raise ValueError(f"status phải là một trong {ALLOWED_STATUS}")
        return v


class MenuItemResponse(BaseModel):
    id: int
    dish_code: str
    dish_name: str
    calorie_count: int
    price: float
    status: str

    model_config = {"from_attributes": True}
