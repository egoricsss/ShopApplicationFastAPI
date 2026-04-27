from decimal import Decimal

from sqlalchemy import create_engine, Integer, String, Numeric, ForeignKey
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    declared_attr,
)


class Base(DeclarativeBase):

    @declared_attr
    def id(cls) -> Mapped[int]:
        return mapped_column(Integer, primary_key=True)


class Customer(Base):

    __tablename__ = "customers"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)

    orders: Mapped[list["Order"]] = relationship(
        "Order", back_populates="customer", uselist=True
    )


class Order(Base):

    __tablename__ = "orders"

    order_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), nullable=False)

    customer: Mapped["Customer"] = relationship(
        "Customer", back_populates="orders", uselist=False
    )


if __name__ == "__main__":
    engine = create_engine("sqlite:///:memory:", echo=True)
    Base.metadata.create_all(engine)
