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
    options: str | None
    price: float
    ski: str | None
    quantity: int


class ProductModel(BaseModel):
    id: int
    title: str
    vendor: str
    product_type: str | None
    tags: str | None
    variants: List[VariantModel]


class ProductResponsse(BaseModel):
    products: List[ProductModel]
