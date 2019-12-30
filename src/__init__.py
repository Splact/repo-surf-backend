from sanic import Sanic

from .middlewares import setup as setup_middlewares
from .views.github import github_app

app = Sanic(__name__)

app.config.from_envvar("REPOSURF_SETTINGS")

app.blueprint(github_app)

setup_middlewares(app)
