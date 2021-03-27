from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine('sqlite:///D:\\С телефона (новое, старое на старом ноуте)\\По учебе\\триместр 10\\web\\pythonAuth\\db\\database.sqlite',
                       convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
base = declarative_base()
base.query = db_session.query_property()


def init_db():
    from entities import models
    models.base.metadata.create_all(bind=engine)
