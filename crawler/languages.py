from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String

Base = declarative_base()


class Languages(Base):
    __tablename__ = 'languages'

    id = Column(Integer, primary_key=True)
    lang = Column(String)
    lines = Column(Integer)

    def __repr__(self):
        return "<User(id='%s', lang='%s', lines='%s')>" % (str(self.id), self.lang, str(self.lines))
