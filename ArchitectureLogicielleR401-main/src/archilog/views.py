import click
import uuid
import io

from flask import Flask, render_template, redirect, url_for, request, send_file

import archilog.models as models
import archilog.services as services

app = Flask(__name__)

@app.route("/home")
def home():
    entries = models.get_all_entries()
    print(entries)
    return render_template("home.html", entries=entries)


@app.route("/update/<uuid:id>", methods=["GET", "POST"])
def update_entry(id):
    entry = models.get_entry(id)

    if request.method == "POST":
        name = request.form["name"]
        montant = float(request.form["montant"])
        category = request.form["category"]

        models.update_entry(id, name, montant, category)
        return redirect(url_for('home'))

    return render_template("update.html", entry=entry)

@app.route("/delete/<uuid:id>")
def delete_entry(id):
    models.delete_entry(id)  
    entries = models.get_all_entries()  # Recharge les entrées
    return render_template("home.html", entries=entries)


@app.route("/create_entry", methods=["GET", "POST"])
def create_entry():
    if request.method == "POST":
        nom = request.form["nom"]
        categorie = request.form["categorie"]
        montant = float(request.form["montant"])

        models.create_entry(nom, montant, categorie)

    return render_template("create.html")

@app.route("/export_csv")
def export_csv():

    csv_stringio = services.export_to_csv()
    csv_string = csv_stringio.getvalue()

    csv_bytes = io.BytesIO()
    csv_bytes.write(csv_string.encode('utf-8'))
    csv_bytes.seek(0)

    return send_file(
        csv_bytes,
        mimetype='text/csv',
        as_attachment=True,
        download_name='fichier_entree.csv'
    )


@app.route("/import_csv", methods=["GET", "POST"])
def import_csv():
    if request.method == "POST":

        fichier = request.files.get("file")

        if not fichier:
            return "Importation ratee!"

        file_stream = io.TextIOWrapper(fichier.stream, encoding='utf-8')
        services.import_from_csv(file_stream)

        return "Importation réussie !"

    return render_template("import_csv.html")


@click.group()
def cli():
    pass


@cli.command()
def init_db():
    models.init_db()


@cli.command()
@click.option("-n", "--name", prompt="Name")
@click.option("-a", "--amount", type=float, prompt="Amount")
@click.option("-c", "--category", default=None)
def create(name: str, amount: float, category: str | None):
    models.create_entry(name, amount, category)


@cli.command()
@click.option("--id", required=True, type=click.UUID)
def get(id: uuid.UUID):
    click.echo(models.get_entry(id))


@cli.command()
@click.option("--as-csv", is_flag=True, help="Ouput a CSV string.")
def get_all(as_csv: bool):
    if as_csv:
        click.echo(services.export_to_csv().getvalue())
    else:
        click.echo(models.get_all_entries())


@cli.command()
@click.argument("csv_file", type=click.File("r"))
def import_csv(csv_file):
    services.import_from_csv(csv_file)


@cli.command()
@click.option("--file", type=click.Path(), default="export.csv", help="Nom du fichier CSV à exporter")
def export_csv(file):
    sortie_csv = services.export_to_csv()
    contenu_csv = sortie_csv.getvalue()
    click.echo(contenu_csv)

    with open(file, "w", newline="") as f:
        click.echo(f"Le fichier a été exporté!")
        f.write(contenu_csv)


@cli.command()
@click.option("--id", type=click.UUID, required=True)
@click.option("-n", "--name", required=True, prompt = "Name")
@click.option("-a", "--amount", type=float, required=True, prompt = "Amount")
@click.option("-c", "--category", default=None)
def update(id: uuid.UUID, name: str, amount: float, category: str | None):
    models.update_entry(id, name, amount, category)


@cli.command()
@click.option("--id", required=True, type=click.UUID)
def delete(id: uuid.UUID):
    models.delete_entry(id)
