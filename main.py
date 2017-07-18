#!/usr/bin/env python

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/core/libs')

import webapp2
import logging
from webapp2_extras import routes
import handler
import core.handler

app = webapp2.WSGIApplication([
    routes.DomainRoute('styleshot-otchy-net.appspot.com', [
        routes.RedirectRoute('/', redirect_to='http://styleshot.otchy.net', schemes=['http'])
    ]),
    ('/', handler.IndexHandler),
    ('/login/', handler.LoginHandler),
    ('/oauth/login/', core.handler.OauthLoginHandler),
    ('/oauth/return/', core.handler.OauthReturnHandler),
    ('/logout/', core.handler.LogoutHandler),
], debug=True)

def handle_error(request, response, exception):
    message = 'Error!'
    if hasattr(exception, 'code'):
        response.set_status(exception.code)
        message = exception
        if exception.code != 404:
            logging.exception('{}: {}'.format(exception.code, exception))
    else:
        response.set_status(500)
        logging.exception(exception.message)
        message = exception.message
    template = core.handler.JINJA_ENVIRONMENT.get_template('error.html')
    response.write(template.render({'message': message}))
 
app.error_handlers[400] = handle_error
app.error_handlers[404] = handle_error
app.error_handlers[405] = handle_error
app.error_handlers[500] = handle_error