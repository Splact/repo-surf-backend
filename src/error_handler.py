from sanic.handlers import ErrorHandler
from sanic.exceptions import SanicException
from sanic.log import logger

class CustomErrorHandler(ErrorHandler):
    def default(self, request, exception):
        if not isinstance(exception, SanicException):
            logger.exception(exception)

        return super().default(request, exception)
