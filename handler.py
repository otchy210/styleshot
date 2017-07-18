import os
import webapp2
import datetime
import jinja2
from core.Response import Response
from core.handler import BaseHandler, AuthHandler

class IndexHandler(AuthHandler):
    def process_get(self):
        return Response().type('html').template('index.html')

class LoginHandler(BaseHandler):
    def process_get(self):
        dest = self.request.get('dest')
        dest = dest if dest else '/'
        return Response().type('html').template('login.html').values({
            'dest': dest
        })