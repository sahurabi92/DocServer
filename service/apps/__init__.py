from flask import Flask
import werkzeug
from config.config import config_server
from .apis import init_api
from .models import db, ma, api

werkzeug.cached_property = werkzeug.utils.cached_property
app = Flask(__name__)


def create_app():
    app.config.from_object(config_server())
    db.init_app(app)
    ma.init_app(app)
    api.init_app(app)
    init_api(api)
    init_logger()
    with app.app_context():
        from .models import DocLib
        db.create_all()
    return app, db


def init_logger():
    import logging
    from logging.config import dictConfig
    from config.config import logging_config
    logging.config.dictConfig(logging_config.log_config)
