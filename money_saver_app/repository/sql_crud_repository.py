from typing import (
    Callable,
    Generic,
    Iterable,
    Optional,
    Type,
    TypedDict,
    TypeVar,
    get_args,
)
from uuid import UUID

from loguru import logger
from sqlalchemy import Engine, create_engine
from sqlmodel import Session, SQLModel, select

T = TypeVar("T", bound=SQLModel)
ID = TypeVar("ID", UUID, int)


class SQLConnectionParam(TypedDict):
    url: str


class SQLCrudRepository(Generic[ID, T]):
    def __init__(self, engine: Engine) -> None:
        self.engine = engine
        self.id_type, self.model_class = self._get_model_id_type_with_class()

    @classmethod
    def create_all_tables(cls, url: str) -> Engine:
        engine = create_engine(
            url, echo=True, json_serializer=lambda model: model.model_dump_json()
        )
        SQLModel.metadata.create_all(engine)
        return engine

    @classmethod
    def _get_model_id_type_with_class(cls) -> tuple[Type[ID], Type[T]]:
        return get_args(tp=cls.__mro__[0].__orig_bases__[0])

    def _commit_operation_in_session(
        self,
        session_operation: Callable[[Session], None],
        session: Session,
        is_commit: bool,
    ) -> bool:
        try:
            session_operation(session)
            if is_commit:
                session.commit()
        except Exception as error:
            logger.error(error)
            return False

        return True

    def _create_session(self) -> Session:
        return Session(self.engine, expire_on_commit=False)

    def find_by_id(self, id: ID, session: Optional[Session] = None) -> Optional[T]:
        if session is None:
            session = self._create_session()

        statement = select(self.model_class).where(self.model_class.id == id)  # type: ignore
        return session.exec(statement).first()

    def find_all_by_ids(
        self, ids: list[ID], session: Optional[Session] = None
    ) -> list[T]:
        if session is None:
            session = self._create_session()
        statement = select(self.model_class).where(self.model_class.id.in_(ids))  # type: ignore
        return list(session.exec(statement).all())

    def find_all(self, session: Optional[Session] = None) -> list[T]:
        if session is None:
            session = self._create_session()
        statement = select(self.model_class)  # type: ignore
        return list(session.exec(statement).all())

    def save(
        self, entity: T, session: Optional[Session] = None, is_commit: bool = True
    ) -> T:
        self._commit_operation_in_session(
            lambda session: session.add(entity),
            session or self._create_session(),
            is_commit,
        )
        return entity

    def save_all(
        self,
        entities: Iterable[T],
        session: Optional[Session] = None,
        is_commit: bool = True,
    ) -> bool:
        return self._commit_operation_in_session(
            lambda session: session.add_all(entities),
            session or self._create_session(),
            is_commit,
        )

    def delete(
        self, entity: T, session: Optional[Session] = None, is_commit: bool = True
    ) -> bool:
        return self._commit_operation_in_session(
            lambda session: session.delete(entity),
            session or self._create_session(),
            is_commit,
        )

    def delete_all(
        self,
        entities: Iterable[T],
        session: Optional[Session] = None,
        is_commit: bool = True,
    ) -> bool:
        session = session or self._create_session()
        for entity in entities:
            session.delete(entity)
        if is_commit:
            session.commit()

        return True
