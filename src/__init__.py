from sanic import Sanic
from sanic.log import logger

from .error_handler import CustomErrorHandler
from .logging_config import LOGGING_CONFIG
from .middlewares import setup as setup_middlewares
from .views.github import github_app


app = Sanic(__name__, log_config=LOGGING_CONFIG)

app.error_handler = CustomErrorHandler()

logger.info('Load configs')
app.config.from_envvar("REPOSURF_SETTINGS")

logger.info('Setup api')
app.blueprint(github_app)

setup_middlewares(app)
