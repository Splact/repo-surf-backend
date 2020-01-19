from src import app
from sanic.log import logger


if __name__ == "__main__":
    logger.info(f'Running server...')
    logger.info(f'\tDebug: {str(app.config["DEBUG"])}')
    logger.info(f'\tWorkers: {app.config["WORKERS"]}')

    app.run(host="0.0.0.0", port=5000, debug=app.config["DEBUG"], access_log=True, workers=app.config["WORKERS"])
