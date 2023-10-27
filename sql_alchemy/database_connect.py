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
        self.uid = Mapped[int](uid)

    def __repr__(self):
        return f"<BotUser(uid={self.uid}, dubai={self.dubai}, doc={self.doc})>"


class BotAdmin(Base):
    __tablename__ = "admins"

    uid: Mapped[int] = mapped_column(Integer, primary_key=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)

    def __init__(self, uid: int, **kw: any):
        super().__init__(**kw)
        self.uid = Mapped[int](uid)

    def __repr__(self):
        return f"<BotAdmin(uid={self.uid}, is_admin={self.is_admin})>"
