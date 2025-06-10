from flask import Flask
from archilog.views.gui import web_ui

def create_app():
    app = Flask(__name__)
    app.register_blueprint(web_ui)
    app.config.from_prefixed_env(prefix="ARCHILOG_FLASK")
    app.config["SECRET_KEY"] = "HAHAHAHAH"
    return app
