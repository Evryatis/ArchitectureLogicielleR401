from flask import Flask
from .gui import web_ui
from .api import api as api_blueprint, spec as api_spec


from flask import Flask, Blueprint



def create_app():
    app = Flask(__name__)
    app.config.from_prefixed_env(prefix="ARCHILOG_FLASK")
    app.config["SECRET_KEY"] = "HAHAHAHAH"

    app.register_blueprint(web_ui)
    app.register_blueprint(api_blueprint, url_prefix="/api")

    return app