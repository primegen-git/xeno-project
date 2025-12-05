from sqlalchemy import BigInteger, ForeignKey
from sqlalchemy.orm import mapped_column, relationship, Mapped
from database import Base, engine
from typing import List


def create_db_and_tables():
    Base.metadata.create_all(engine)


class Dummy(Base):
    __tablename__ = "dummy"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    message: Mapped[str] = mapped_column()


class Tenant(Base):
    __tablename__ = "tenants"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    shop: Mapped[str] = mapped_column(unique=True, nullable=False)
    access_token: Mapped[str] = mapped_column(unique=True, nullable=False)

    # owner: Mapped["Owner"] = relationship(
    #     "Owner",
    #     back_populates="tenant",
    #     uselist=False,
    #     cascade="all, delete-orphan",
    #     passive_deletes=True,
    # )

    product: Mapped[List["Product"]] = relationship(
        "Product",
        back_populates="tenant",
        uselist=True,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    customer: Mapped[List["Customer"]] = relationship(
        "Customer",
        back_populates="tenant",
        uselist=True,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


# class Owner(Base):
#     __tablename__ = "owners"
#
#     id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
#     email: Mapped[str] = mapped_column(unique=True, nullable=False)
#     hashed_password: Mapped[str] = mapped_column(nullable=False)
#
#     tenant_id: Mapped[int] = mapped_column(
#         ForeignKey("tenants.id", ondelete="CASCADE"),
#         unique=True,
#         nullable=False,
#     )
#
#     tenant: Mapped["Tenant"] = relationship(
#         "Tenant",
#         back_populates="owner",
#     )
#


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    title: Mapped[str] = mapped_column()
    vendor: Mapped[str] = mapped_column()
    product_type: Mapped[str] = mapped_column()
    tags: Mapped[str] = mapped_column()
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"))

    tenant: Mapped["Tenant"] = relationship("Tenant", back_populates="product")

    variant: Mapped[List["Variant"]] = relationship(
        "Variant",
        uselist=True,
        back_populates="product",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class Variant(Base):
    __tablename__ = "variants"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    options: Mapped[str] = mapped_column()
    price: Mapped[float] = mapped_column(default=0.0)
    sku: Mapped[str] = mapped_column()
    quantity: Mapped[str] = mapped_column()
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE")
    )

    product: Mapped["Product"] = relationship("Product", back_populates="variant")


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    first_name: Mapped[str] = mapped_column()
    last_name: Mapped[str] = mapped_column()
    email: Mapped[str] = mapped_column()
    verified_email: Mapped[bool] = mapped_column(default=False)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"))

    tenant: Mapped["Tenant"] = relationship("Tenant", back_populates="customer")

    addresses: Mapped[List["Address"]] = relationship(
        "Address",
        uselist=True,
        cascade="all, delete-orphan",
        passive_deletes=True,
        back_populates="customer",
    )


class Address(Base):
    __tablename__ = "addresses"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    address1: Mapped[str] = mapped_column()
    city: Mapped[str] = mapped_column()
    province: Mapped[str] = mapped_column()
    zip: Mapped[int] = mapped_column()
    country: Mapped[str] = mapped_column()
    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.id", ondelete="CASCADE")
    )

    customer: Mapped["Customer"] = relationship("Customer", back_populates="addresses")
