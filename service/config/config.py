import os

base_dir = os.path.abspath(os.path.dirname(__file__))
db_dir = os.path.join(base_dir, '../db', 'bookServer.db')
file_dir = os.path.join(base_dir, "../", 'files')
log_file = os.path.join(base_dir, "../", 'logs', 'book_event_log.log')


class config_server(object):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + db_dir
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = file_dir
    ALLOWED_EXTENSIONS = {'txt', 'xlsx'}


class logging_config:
    log_config = {
        "version": 1,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] - %(levelname)s-%(message)s"
            }
        },
        "handlers": {
            "log_file": {
                "class": "logging.FileHandler",
                "formatter": "default",
                "level": "INFO",
                'filename': log_file,
                "delay": "True",
            }

        },
        "loggers": {
            "default": {
                "handlers": ["log_file"],
                "level": 'INFO',
                "propagate": False,
            }
        }

    }
