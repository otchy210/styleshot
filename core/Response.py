import json

class Response:
    def __init__(self):
        self._status = Response.Status.OK
        self._type = None
        self._template = None
        self._values = {}

    def status(self, status = None):
        if status is None:
            return self._status
        self._status = status
        return self

    def type(self, type = None):
        if type is None:
            return self._type
        self._type = type
        return self

    def template(self, template = None):
        if template is None:
            return self._template
        self._template = template
        return self

    def values(self, values = None):
        if values is None:
            return self._values
        self._values = values
        return self

    def location(self, location = None):
        if location is None:
            return self._values['location']
        self._values['location'] = location
        return self

    def redirect_permanently(self, location):
        return self.redirect(Response.Status.MOVED_PERMANENTLY, location)

    def redirect_temporarily(self, location):
        return self.redirect(Response.Status.MOVED_TEMPORARILY, location)

    def redirect(self, status, location):
        return self.type('redirect').status(status).location(location)

    class Status:
        OK = 200
        MOVED_PERMANENTLY = 301
        MOVED_TEMPORARILY = 302
        BAD_REQUEST = 400
        NOT_FOUND = 404
        METHOD_NOT_ALLOWED = 405
