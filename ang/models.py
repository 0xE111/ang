import humps
# from sqlalchemy import *  # noqa - expose sqlalchemy interface
# import sqlalchemy.orm  # noqa
from sqlalchemy import BigInteger, Column
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import synonym
# from sqlalchemy.ext.hybrid import hybrid_property

# from envparse import env
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy.ext.asyncio import create_async_engine
# engine = sqlalchemy.create_engine(env('DATABASE_URL'))
# Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)


class Base:

    @declared_attr
    def __tablename__(self) -> str:
        name = humps.decamelize(self.__class__.__name__)
        if not name.endswith('s'):
            name += 's'
        return name

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
