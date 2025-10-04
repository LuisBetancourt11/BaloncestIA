from app.db import SessionLocal, engine
from app import models

models.Base.metadata.create_all(bind=engine)

if __name__=='__main__':
    db = SessionLocal()
    u = models.User(name='Demo')
    db.add(u)
    db.commit()
    print('Seed created user id', u.id)
