"""
Fixtures de pruebas. Usan SQLite en memoria: validan la lógica de los
repositorios y las restricciones CHECK/UNIQUE/FK declaradas en los modelos
sin necesidad de SQL Server. Las pruebas contra SQL Server real se hacen
con scripts/check_models.py.
"""

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
import app.models  # noqa: F401  (registra los modelos en Base.metadata)


@pytest.fixture()
def db():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )

    @event.listens_for(engine, "connect")
    def _fk_on(dbapi_connection, _):
        dbapi_connection.execute("PRAGMA foreign_keys=ON")

    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine, autoflush=False)()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()
