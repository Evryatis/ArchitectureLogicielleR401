import uuid
from datetime import datetime

from archilog.config import config

from sqlalchemy import create_engine,Table, MetaData, Column, String, Float, Uuid, select, DateTime, func, delete, update

from dataclasses import dataclass


engine = create_engine(config.DATABASE_URL, echo=config.DEBUG)
metadata = MetaData()

sql_alchemy_data = Table(
    "entries",
    metadata,
    Column("id", Uuid, primary_key = True, default=uuid.uuid4),
    Column("name", String, nullable = False),
    Column("date", DateTime, nullable = False, default=func.now()),
    Column("montant", Float, nullable = False),
    Column("categorie", String, nullable = True)
)



def init_db():
    metadata.create_all(engine)

@dataclass
class Entry:

    id: uuid.UUID
    name: str
    date : datetime
    montant: float
    categorie: str | None

def create_entry(name: str, montant: float, categorie: str | None = None) -> None:

    with engine.begin() as conn:

        sql_stmt = sql_alchemy_data.insert().values(name=name, montant=montant, categorie=categorie)
        conn.execute(sql_stmt)


def get_entry(id: uuid.UUID) -> Entry:
    
    sql_stmt = select(sql_alchemy_data).where(sql_alchemy_data.c.id == id)

    with engine.begin() as conn:

        execute = conn.execute(sql_stmt)
        resultat = execute.fetchone()

        if resultat:
            return Entry(resultat.id, resultat.name, resultat.date, resultat.montant, resultat.categorie)
        else:
            raise Exception("Entry not found")


def get_all_entries() -> list[Entry]:
    sql_stmt = select(sql_alchemy_data)
    
    with engine.begin() as conn:
        results = conn.execute(sql_stmt).fetchall()
        return [Entry(*r) for r in results]


def update_entry(id: uuid.UUID, name: str, montant: float, categorie: str | None) -> None:
    sql_stmt = update(sql_alchemy_data).where(sql_alchemy_data.c.id == id).values(name=name, montant=montant, categorie=categorie)
    
    with engine.begin() as conn:
        conn.execute(sql_stmt)


def delete_entry(id: uuid.UUID) -> None:
    sql_stmt = delete(sql_alchemy_data).where(sql_alchemy_data.c.id == id)    
    
    with engine.begin() as conn:
        conn.execute(sql_stmt)