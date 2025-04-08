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

