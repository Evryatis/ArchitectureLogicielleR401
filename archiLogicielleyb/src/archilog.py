import click
import uuid
import sqlite3

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
@click.option("-d", "--deposit", prompt="Montant du dépot", type=int, help="Le montant que vous souhaitez déposer")
@click.option("-c", "--database", prompt="Nom de la BD", type=str, help="La base de donnée à laquelle vous souhaitez vous connecter")
def addDeposit(deposit: int, database: str):
    id_depot = str(uuid.uuid4())
    connexion = sqlite3.connect(database)
    curseur = connexion.cursor()
    curseur.execute("INSERT INTO deposits (id, name, deposit) VALUES (?, ?, ?)", (id_depot, "Depot", deposit))
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

if __name__ == "__main__":
    cli()
