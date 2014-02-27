from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date
Base = declarative_base()


class Repository(Base):
    __tablename__ = 'repository'

    id = Column(Integer, primary_key=True)
    full_name = Column(String)
    languages_url = Column(String)
    creation_date = Column(Date)

    def __repr__(self):
        return "<User(id='%s', full_name='%s', creation_date='%s', languages_url = '%s')>" % (
        str(self.id), self.full_name, str(self.creation_date), languages_url)
