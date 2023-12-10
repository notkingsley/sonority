from sqlalchemy.orm import Mapped, mapped_column

from sonority.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column()
    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    pwd_hash: Mapped[str] = mapped_column(nullable=False)