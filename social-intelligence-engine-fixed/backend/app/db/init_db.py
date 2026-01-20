from app.db.base import Base
from app.db.database import engine

# Import models to register metadata
from app.db import models  # noqa: F401


def init_db():
    Base.metadata.create_all(bind=engine)
