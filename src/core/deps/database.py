from contextlib import AbstractContextManager, contextmanager
from typing import Callable

from sqlalchemy import create_engine, orm
from sqlalchemy.orm import DeclarativeBase, Session

from src.core.config import Settings
from src.core.deps.logger import with_logger


class Base(DeclarativeBase):
    pass


class MySQLBase(DeclarativeBase):
    pass


@with_logger()
class Database:
    def __init__(self, config: Settings) -> None:
        self._engine = create_engine(
            self.create_url(config),
            echo=False,
            pool_recycle=config["DB_POOL_RECYCLE"],
            pool_pre_ping=config["DB_POOL_PRE_PING"],
        )
        self._session_factory = orm.scoped_session(
            orm.sessionmaker(
                autocommit=False, autoflush=False, bind=self._engine
            ),
        )

    def create_url(self, settings: Settings) -> str:
        return (
            settings["DB_DIALECT"]
            + "://"
            + settings["DB_USER"]
            + ":"
            + settings["DB_PASSWORD"]
            + "@"
            + settings["DB_HOST"]
            + ":"
            + str(settings["DB_PORT"])
            + "/"
            + settings["DB_DATABASE"]
        )

    @property
    def engine(self):
        return self._engine

    @contextmanager
    def session(self) -> Callable[..., AbstractContextManager[Session]]:
        session: Session = self._session_factory()
        self._logger.debug("[DB] Session created")
        try:
            yield session
        except Exception:
            self._logger.warning("[DB] Session rollback because of exception")
            session.rollback()
            raise
        finally:
            session.close()


@with_logger()
class MysqlDatabase:
    def __init__(self, config: Settings) -> None:
        self._engine = create_engine(
            self.create_url(config),
            echo=False,
            pool_recycle=config["MYSQL_DB_POOL_RECYCLE"],
            pool_pre_ping=config["MYSQL_DB_POOL_PRE_PING"],
        )
        self._session_factory = orm.scoped_session(
            orm.sessionmaker(
                autocommit=False, autoflush=False, bind=self._engine
            ),
        )

    def create_url(self, settings: Settings) -> str:
        return (
            settings["MYSQL_DB_DIALECT"]
            + "://"
            + settings["MYSQL_DB_USER"]
            + ":"
            + settings["MYSQL_DB_PASSWORD"]
            + "@"
            + settings["MYSQL_DB_HOST"]
            + ":"
            + str(settings["MYSQL_DB_PORT"])
            + "/"
            + settings["MYSQL_DB_DATABASE"]
        )

    @property
    def engine(self):
        return self._engine

    @contextmanager
    def session(self) -> Callable[..., AbstractContextManager[Session]]:
        session: Session = self._session_factory()
        self._logger.debug("[MySQL-DB] Session created")
        try:
            yield session
        except Exception:
            self._logger.warning(
                "[MySQL-DB] Session rollback because of exception"
            )
            session.rollback()
            raise
        finally:
            session.close()
