from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date
Base = declarative_base()


class Repository(Base):
    __tablename__ = 'repository'

    id = Column(Integer, primary_key=True)
    full_name = Column(String)
    languages_url = Column(String)
    creation_date = Column(Date)
    main_lang = Column(String)
    username = Column(String)
    size = Column(Integer)
    stargazers_count = Column(Integer)
    watchers_count = Column(Integer)
    subscribers_count  = Column(Integer)
    forks_count = Column(Integer)
    open_issues_count = Column(Integer)

    def __repr__(self):
        return "<User(id='%s', full_name='%s', creation_date='%s', languages_url = '%s')>" % (
        str(self.id), self.full_name, str(self.creation_date), languages_url)

    @staticmethod
    def update(session, sid, **kargs):
        repo = session.query(Repository).filter_by(id=sid).first()

        if repo is not None:
            if 'full_name' in kargs:
                repo.full_name = kargs['full_name']

            if 'languages_url' in kargs:
                repo.languages_url = kargs['languages_url']

            if 'creation_date' in kargs:
                repo.creation_date = kargs['creation_date']

            if 'main_lang' in kargs:
                repo.main_lang = kargs['main_lang']

            if 'size' in kargs:
                repo.size = kargs['size']
                

            if 'stargazers_count' in kargs:
                repo.stargazers_count = kargs['stargazers_count']

            if 'watchers_count' in kargs:
                repo.watchers_count = kargs['watchers_count']

            if 'subscribers_count' in kargs:
                repo.subscribers_count = kargs['subscribers_count']

            if 'forks_count' in kargs:
                repo.forks_count = kargs['forks_count']

            if 'open_issues_count' in kargs:
                repo.open_issues_count = kargs['open_issues_count']

            session.add(repo)
            return True
        else:
            return False
