from pydantic import BaseModel
from typing import List, Dict


class AddressModel(BaseModel):
    id: int
    address1: str
    city: str
    province: str
    zip: int
    country: str


class CustomerModel(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    verified_email: bool
    addresses: List[AddressModel]


class CustomerResponse(BaseModel):
    customers: List[CustomerModel]
