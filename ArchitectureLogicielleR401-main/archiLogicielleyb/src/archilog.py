import click
import uuid
import sqlite3
import csv

from testpackage.raa import printrahh

from dataclasses import dataclass


@dataclass
class Item:
    id: uuid.UUID
    name: str
    deposit: int = 0


@click.group()
def cli():
     pass



@cli.command()
@click.option("-c", "--connect", prompt="Connexion a la base de donnée", type=str, help="Veuillez indiquez la base de donnée")
def connectdatabase(connect: str):
    connexion = sqlite3.connect(connect)
    connexion.execute("""CREATE TABLE IF NOT EXISTS deposits (
                            id TEXT PRIMARY KEY, 
                            name TEXT NOT NULL,
                            deposit INTEGER NOT NULL
                            )
                        """)
    connexion.commit()
    connexion.close()



@cli.command()
@click.option("-n", "--name", prompt="Name", help="The name of the item.")
def display(name: str):
    item = Item(uuid.uuid4(), name)
    click.echo(item)

@cli.command()
@click.option("-d", "--deposit", prompt="Montant de la transaction", type=int, help="Le montant que vous souhaitez transferer")
@click.option("-o", "--name", prompt="Raison de la transaction?", type=str, help="Raison de la transaction")
@click.option("-c", "--database", prompt="Nom de la BD", type=str, help="La base de donnée à laquelle vous souhaitez vous connecter")
def addDeposit(deposit: int, database: str, name: str):
    id_depot = str(uuid.uuid4())
    connexion = sqlite3.connect(database)
    curseur = connexion.cursor()
    curseur.execute("INSERT INTO deposits (id, name, deposit) VALUES (?, ?, ?)", (id_depot, name, deposit))
    connexion.commit()
    connexion.close()

                        
@cli.command
@click.option("-c", "--database", prompt="Nom de la BD", type=str, help="La base de donnée à laquelle vous souhaitez vous connecter")
def showdeposit(database: str):
    connexion = sqlite3.connect(database)
    row = connexion.execute("SELECT * FROM deposits").fetchone()
    click.echo(row)
    connexion.commit()
    connexion.close()


@cli.command
@click.option("-c", "--database", prompt="Nom de la BD", type=str, help="La base de donnée à laquelle vous souhaitez vous connecter")
@click.option("-d", "--delete", type=str, prompt="Nom de la transaction que vous souhaitez effacer")
def delete(delete: str, database: str):
    connexion = sqlite3.connect(database)
    connexion.execute("DELETE FROM deposits WHERE name = ?", (delete,))
    connexion.commit()
    connexion.close()
    click.echo(f"Transaction '{delete}' deleted from the database.")


@cli.command()
@click.option("-c", "--csvfile", prompt="Nom du fichier CSV que vous souhaitez charger en base de donnée ", type=str, help="Nom du fichier CSV")
@click.option("-d", "--database", prompt="Nom de la BD", type=str,help="Le nom de la base de donnée à laquelle vous souhaitez vous connecter")
def csvdata(csvfile: str, database: str):

    connexion = sqlite3.connect(database)

    with open(csvfile, mode='r', newline='', encoding='utf-8') as file:
        csv_reader = csv.reader(file)
        ligne_dessus = next(csv_reader)

        for row in csv_reader:

            connexion.execute("INSERT INTO deposits (id, name, deposit) VALUES (?, ?, ?)",(row[0], row[1], row[2]))  # Assuming CSV has two columns: name and deposit

    connexion.commit()
    connexion.close()

    click.echo(f"Le fichier {csvfile} a été chargé avec succès dans la base de données.")

#MODEL FOR WHATEVER

import sqlite3
import uuid
from sqlalchemy import create_engine, MetaData, Column, String, Float, Table
from dataclasses import dataclass

# Database config
DB_URL = "data.db"
db = None

# SQLAlchemy setup
engine = create_engine(f"sqlite:///{DB_URL}", echo=True)
metadata = MetaData()

entries_table = Table(
    "entries",
    metadata,
    Column("id", String, primary_key=True),
    Column("name", String, nullable=False),
    Column("amount", Float, nullable=False),
    Column("category", String, nullable=True),
)

def get_db():
    global db
    if db is None:
        db = sqlite3.connect(DB_URL)
    return db

def init_db():
    metadata.create_all(engine)

@dataclass
class Entry:
    id: uuid.UUID
    name: str
    amount: float
    category: str | None

    @classmethod
    def from_db(cls, id: str, name: str, amount: float, category: str | None):
        return cls(uuid.UUID(id), name, amount, category)

def create_entry(name: str, amount: float, category: str | None = None) -> Entry:
    new_id = str(uuid.uuid4())
    with engine.begin() as conn:
        stmt = entries_table.insert().values(
            id=new_id,
            name=name,
            amount=amount,
            category=category
        )
        conn.execute(stmt)
    return Entry(uuid.UUID(new_id), name, amount, category)

def get_entry(id: uuid.UUID) -> Entry:
    with get_db() as db_conn:
        result = db_conn.execute(
            entries_table.select(entries_table).where(entries_table.id == id)
        ).fetchone()
        if result:
            return Entry.from_db(*result)
        else:
            raise Exception("Entry not found")

def get_all_entries() -> list[Entry]:
    with get_db() as db_conn:
        results = db_conn.execute(
            "SELECT id, name, amount, category FROM entries"
        ).fetchall()
        return [Entry.from_db(*r) for r in results]

def update_entry(id: uuid.UUID, name: str, amount: float, category: str | None) -> None:
    with get_db() as db_conn:
        db_conn.execute(
            "UPDATE entries SET name = ?, amount = ?, category = ? WHERE id = ?",
            (name, amount, category, str(id))
        )
        db_conn.commit()

def delete_entry(id: uuid.UUID) -> None:
    with get_db() as db_conn:
        db_conn.execute(
            "DELETE FROM entries WHERE id = ?", (str(id),)
        )
        db_conn.commit()



