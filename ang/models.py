from importlib import import_module

import humps
from sqlalchemy import BigInteger, Column
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import sessionmaker, synonym


class Base:

    @declared_attr
    def __tablename__(self) -> str:
        name = humps.decamelize(self.__class__.__name__)
        if not name.endswith('s'):
            name += 's'
        return name

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


settings = import_module('settings')
engine = create_async_engine(settings.DATABASE_URL, echo=True)
session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
