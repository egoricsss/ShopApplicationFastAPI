from datetime import date

from sqlalchemy import Integer, String, Date, func, ForeignKey
from sqlalchemy.schema import CreateTable
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    declared_attr,
)


class Base(DeclarativeBase):
    pass


class IdMixin:
    @declared_attr
    def id(cls) -> Mapped[int]:
        return mapped_column(Integer, primary_key=True)


class Participation(Base):
    __tablename__ = "participations"
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), primary_key=True)
    employee_id: Mapped[int] = mapped_column(
        ForeignKey("employees.id"), primary_key=True
    )
    role: Mapped[str] = mapped_column(String(50), nullable=False)


class Project(Base, IdMixin):
    __tablename__ = "projects"

    name: Mapped[str] = mapped_column(String(150), nullable=False)
    start_date: Mapped[date] = mapped_column(
        Date, server_default=func.now(), nullable=False
    )

    employees: Mapped[list["Employee"]] = relationship(
        back_populates="projects", secondary="participations"
    )


class Employee(Base, IdMixin):
    __tablename__ = "employees"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)

    projects: Mapped[list["Project"]] = relationship(
        back_populates="employees", secondary="participations"
    )


if __name__ == "__main__":
    print(CreateTable(Participation.__table__))
    print(CreateTable(Project.__table__))
    print(CreateTable(Employee.__table__))
