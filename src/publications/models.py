from datetime import datetime

from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import Integer, String, func, ForeignKey, UniqueConstraint

from src.database import Base


class Publication(Base):
    __tablename__ = 'publications'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    content: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=datetime.now, nullable=False
    )

    creator_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))


class Vote(Base):
    __tablename__ = 'votes'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    publication_id: Mapped[int] = mapped_column(Integer, ForeignKey("publications.id"))
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    grade: Mapped[bool] = mapped_column(nullable=False)

    __table_args__ = (
        UniqueConstraint("publication_id", "user_id"),
    )
