from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import declarative_base
from sqlalchemy.engine import create_engine

import settings

engine = create_engine('postgresql://{user}:{passwd}@{host}:{port}/{db}'.format(
    user=settings.PSQL_USER,
    passwd=settings.PSQL_PASS,
    host=settings.PSQL_HOST,
    port=settings.PSQL_PORT,
    db=settings.PSQL_DB,
))

Base = declarative_base()


class News(Base):
    __tablename__ = 'news'

    id = Column(Integer, primary_key=True)
    author = Column(String())
    title = Column(String())
    body = Column(String())
    source = Column(String())
