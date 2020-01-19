from sanic.handlers import ErrorHandler
from sanic.exceptions import SanicException

class CustomErrorHandler(ErrorHandler):
    def default(self, request, exception):
        # Some exceptions are trivial and built into Sanic (404s, etc)
        if not isinstance(exception, SanicException):
            print(exception)

        return super().default(request, exception)
