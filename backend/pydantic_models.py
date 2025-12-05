from pydantic import BaseModel
from typing import List


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


class VariantModel(BaseModel):
    id: int
    options: str
    price: float
    ski: str
    quantity: int


class ProductModel(BaseModel):
    id: int
    title: str
    vendor: str
    product_type: str
    tags: bool
    variants: List[VariantModel]


class ProductResponsse(BaseModel):
    products: List[ProductModel]
