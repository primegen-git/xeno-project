from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column, relationship, Mapped
from database import Base, engine


def create_db_and_tables():
    Base.metadata.create_all(engine)


class Dummy(Base):
    __tablename__ = "dummy"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    message: Mapped[str] = mapped_column()


class Tenant(Base):
    __tablename__ = "tenants"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    domain: Mapped[str] = mapped_column(unique=True, nullable=False)
    access_token: Mapped[str] = mapped_column(unique=True, nullable=False)

    owner: Mapped["Owner"] = relationship(
        "Owner",
        back_populates="tenant",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class Owner(Base):
    __tablename__ = "owners"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(nullable=False)

    tenant_id: Mapped[int] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )

    tenant: Mapped["Tenant"] = relationship(
        "Tenant",
        back_populates="owner",
    )
