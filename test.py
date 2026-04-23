from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, declared_attr


class Base(DeclarativeBase):
    @declared_attr
    def id(cls) -> Mapped[int]:
        return mapped_column(Integer, primary_key=True)


class Author(Base):

    __tablename__ = "authors"

    name: Mapped[str] = mapped_column(String(100), nullable=False)

    books: Mapped[list["Book"]] = relationship(
        "Book", back_populates="author", cascade="all, delete orphan"
    )


class Book(Base):

    __tablename__ = "books"

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    author_id: Mapped[int] = mapped_column(
        ForeignKey("authors.id", ondelete="CASCADE"), nullable=False
    )

    author: Mapped["Author"] = relationship("Author", back_populates="books")
