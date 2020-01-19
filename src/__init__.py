import sys
from sanic import Sanic
from sanic.log import logger

from .middlewares import setup as setup_middlewares
from .views.github import github_app

LOGGING_CONFIG = dict(
    version = 1,
    disable_existing_loggers = False,
    loggers = {
        "sanic.root": {"level": "INFO", "handlers": ["console", "info_rotating_file"]},
        "sanic.error": {
            "level": "INFO",
            "handlers": ["error_console", "info_rotating_file"],
            "propagate": True,
            "qualname": "sanic.error",
        },
        "sanic.access": {
            "level": "INFO",
            "handlers": ["access_console", "info_rotating_file"],
            "propagate": True,
            "qualname": "sanic.access",
        },
    },
    handlers = {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "generic",
            "stream": sys.stdout,
        },
        "error_console": {
            "class": "logging.StreamHandler",
            "formatter": "generic",
            "stream": sys.stderr,
        },
        "access_console": {
            "class": "logging.StreamHandler",
            "formatter": "access",
            "stream": sys.stdout,
        },
        'info_rotating_file': {
            'formatter': 'generic',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/info.log',
            'mode': 'a',
            'maxBytes': 1048576,
            'backupCount': 7
        },
    },
    formatters={
        "generic": {
            "format": "%(asctime)s [%(process)d] [%(levelname)s] %(message)s",
            "datefmt": "[%Y-%m-%d %H:%M:%S %z]",
            "class": "logging.Formatter",
        },
        "access": {
            "format": "%(asctime)s - (%(name)s)[%(levelname)s][%(host)s]: "
            + "%(request)s %(message)s %(status)d %(byte)d",
            "datefmt": "[%Y-%m-%d %H:%M:%S %z]",
            "class": "logging.Formatter",
        },
    }
)


app = Sanic(__name__, log_config=LOGGING_CONFIG)

logger.info('Load configs')
app.config.from_envvar("REPOSURF_SETTINGS")

logger.info('Setup api')
app.blueprint(github_app)

setup_middlewares(app)
