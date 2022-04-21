from contextlib import contextmanager
from typing import Optional
from sqlalchemy import Column, Boolean, String, Integer, create_engine, literal
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from src.settings import get_settings
from src.models import User

settings = get_settings()
enigne = create_engine(f"sqlite:///{settings.db_name}", echo=True)

Base = declarative_base()
Session = sessionmaker(enigne)


class DBAdapter:
    @contextmanager
    def get_session(self):
        try:
            session = Session()
            yield session
        except:
            session.rollback()
            raise
        else:
            session.commit()
        finally:
            session.close()


class DBUser(Base):
    __tablename__ = "user"
    telegram_id = Column("id", Integer, primary_key=True)
    credentials = Column("credentials", String, nullable=True)
    is_finished = Column("is_finished", Boolean, default=False)


class UserRepository:
    def __init__(self) -> None:
        self._db_adapter = DBAdapter()

    def get_or_create(self, id: str) -> User:
        with self._db_adapter.get_session() as session:
            q = session.query(DBUser).filter_by(telegram_id=id)
            is_user = session.query(literal(True)).filter(q.exists()).scalar()
            if not is_user:
                user = DBUser(telegram_id=id)
                session.add(user)

            user = User.parse_obj(q.one_or_none().__dict__)
            return user

    def get(self, id: str) -> Optional[User]:
        with self._db_adapter.get_session() as session:
            user = session.query(DBUser).filter_by(telegram_id=id).one_or_none()
            if user:
                user = User.parse_obj(user.__dict__)
            return user

    def update(self, id: str, **kwargs) -> None:
        with self._db_adapter.get_session() as session:
            update_fields = {getattr(DBUser, k): v for k, v in kwargs.items()}
            session.query(DBUser).filter_by(telegram_id=id).update(update_fields)

    def delete(self, id: str) -> None:
        with self._db_adapter.get_session() as session:
            session.query(DBUser).filetr_by(telegram_id=id).delete()
