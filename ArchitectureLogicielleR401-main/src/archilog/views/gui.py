from asyncio import wait_for

from flask import Blueprint, render_template, request, redirect, url_for, send_file, flash
import io

from .. import models as models
from .. import services as services

from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, IntegerField, validators

from flask import Flask
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from wtforms.fields.simple import PasswordField

web_ui = Blueprint("web_ui", __name__)

auth = HTTPBasicAuth()

users = {
    "john": generate_password_hash("hello"),
    "susan": generate_password_hash("bye"),
    "yann":generate_password_hash("mdpyann")
}

class EntryForm(FlaskForm):
    name = StringField('Name', validators=[validators.DataRequired()])
    montant = FloatField('Montant', validators=[validators.DataRequired()])
    category = StringField('Category', validators=[validators.DataRequired()])

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[validators.DataRequired()])
    password = PasswordField('Password', validators=[validators.DataRequired()])

@auth.verify_password
def verify_password(username, password):
    if username in users and check_password_hash(users.get(username), password):
        return username

@web_ui.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        if username and verify_password(username, password):
            flash("Connexion réussie !", "success")
            return redirect(url_for("web_ui.home"))
        else:
            flash("Nom d'utilisateur ou mot de passe incorrect", "danger")
    return render_template("login.html", form=form)

@web_ui.route("/home")
@auth.login_required  # <-- Add this decorator
def home():
    entries = models.get_all_entries()
    return render_template("home.html", entries=entries, user=auth.current_user)

@web_ui.route("/update/<uuid:id>", methods=["GET", "POST"])
def update_entry(id):
    entry = models.get_entry(id)
    if entry is None:
        return "Entry not found", 404

    form = EntryForm(obj=entry)

    if form.validate_on_submit():
        name = form.name.data
        amount = form.montant.data
        category = form.category.data

        models.update_entry(id, name, amount, category)
        return redirect(url_for("web_ui.home"))

    return render_template("update.html", form=form, entry=entry)


@web_ui.route("/delete/<uuid:id>")
def delete_entry(id):
    models.delete_entry(id)
    return redirect(url_for("web_ui.home"))


@web_ui.route("/yann")
@auth.login_required(role="yann")
def admins_only():
    return f"Hello {auth.current_user()}, you are an admin!"

@web_ui.route("/create_entry", methods=["GET", "POST"])
def create_entry():
    form = EntryForm()
    if form.validate_on_submit():
        models.create_entry(form.name.data, form.montant.data, form.category.data)
        return redirect(url_for("web_ui.home"))

    return render_template("create.html", form=form)

@web_ui.route("/export_csv")
def export_csv():
    csv_stringio = services.export_to_csv()
    csv_string = csv_stringio.getvalue()

    csv_bytes = io.BytesIO()
    csv_bytes.write(csv_string.encode("utf-8"))
    csv_bytes.seek(0)

    return send_file(
        csv_bytes,
        mimetype="text/csv",
        as_attachment=True,
        download_name="fichier_entree.csv"
    )

@web_ui.route("/import_csv", methods=["GET", "POST"])
def import_csv():
    if request.method == "POST":
        fichier = request.files.get("file")
        if not fichier:
            return "Importation ratée !"
        file_stream = io.TextIOWrapper(fichier.stream, encoding="utf-8")
        services.import_from_csv(file_stream)
        return redirect(url_for("web_ui.home"))

    return render_template("import_csv.html")
