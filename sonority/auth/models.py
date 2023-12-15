from uuid import uuid4, UUID

from sqlalchemy.orm import Mapped, mapped_column

from sonority.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    email: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column()
    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    pwd_hash: Mapped[str] = mapped_column(nullable=False)