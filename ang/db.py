from importlib import import_module

import humps
from sqlalchemy import BigInteger, Column
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import sessionmaker, synonym

from ang.config import SETTINGS_MODULE


class Base:

    @declared_attr
    def __tablename__(self) -> str:
        assert '.' in self.__module__, f'Unexpected module name for {self}: "{self.__module__}"'
        app = self.__module__.split('.')[0]

        name = humps.decamelize(self.__name__)
        if not name.endswith('s'):
            name += 's'

        return f'{app}_{name}'

    __mapper_args__ = {"eager_defaults": True}

    @declared_attr
    def id(cls):
        """ Return first primary key column, or create a new one. """

        for attr in dir(cls):
            if attr == 'id' or attr.startswith('__'):
                continue

            val = getattr(cls, attr)
            if isinstance(val, Column) and val.primary_key:
                return synonym(attr)

        return Column(BigInteger, primary_key=True, index=True)


Model = declarative_base(cls=Base)


settings = import_module(SETTINGS_MODULE)
engine = create_async_engine(settings.DATABASE_URL, echo=True)
get_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
