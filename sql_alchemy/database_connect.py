from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import func, Table, Column, Integer, Boolean, BigInteger, Sequence
from sqlalchemy.orm import Mapped, mapped_column, registry, DeclarativeBase

mapper_registry = registry()


class Base(DeclarativeBase):
    pass


class BotUser(Base):
    __tablename__ = "subscriptions"

    uid: Mapped[int] = mapped_column(Integer, primary_key=True)
    dubai: Mapped[bool] = mapped_column(Boolean, default=False)
    doc: Mapped[bool] = mapped_column(Boolean, default=False)

    def __init__(self, uid: int, **kw: any):
        super().__init__(**kw)
        self.uid = uid

    def __repr__(self):
        return f"<Chat(id={self.id}, telegram_chat_id={self.telegram_chat_id}, added_on={self.added_on})>"
