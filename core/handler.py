import os
import webapp2
import jinja2
import json
import datetime
import urllib
import httplib2
import uuid

from google.appengine.ext import ndb

import config
import model
from Response import Response
from Session import Session
from oauth2client.client import OAuth2WebServerFlow

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader('/'.join(os.path.dirname(__file__).split('/')[:-1]) + '/template'),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True
)

OAUTH_PROVIDERS = {
    'google': {
        'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
        'token_uri': 'https://accounts.google.com/o/oauth2/token',
        'scope': 'https://www.googleapis.com/auth/userinfo.profile',
        'userinfo_uri': 'https://www.googleapis.com/oauth2/v1/userinfo'
    }
}

class BaseHandler(webapp2.RequestHandler):
    def before_get(self):
        pass

    def get(self):
        self.before_get()
        res = self.process_get()
        self._process(res)
        self.after_get()

    def after_get(self):
        pass

    def before_post(self):
        pass

    def post(self):
        if self.has_invalid_csrf_token():
            self._process(Response().status(Response.Status.BAD_REQUEST))
            return
        self.before_post()
        res = self.process_post()
        self._process(res)
        self.after_post()

    def after_post(self):
        pass

    def has_invalid_csrf_token(self):
        valid_csrf_token = self.session().csrf_token
        req_csrf_token = self.request.get('csrf_token')
        return (valid_csrf_token != req_csrf_token)
        if valid_csrf_token != req_csrf_token:
            return 
        return False

    def before_process(self):
        pass

    def _process(self, res):
        self.before_process()
        self.save_session()
        self.response.status_int = res.status()
        if res.type() == 'html':
            self.render_html(res)
        elif res.type() == 'json':
            self.render_json(res)
        elif res.type() == 'redirect':
            self.redirect(res)
        self.after_process()

    def after_process(self):
        pass

    def process_get(self):
        return Response().status(Response.Status.METHOD_NOT_ALLOWED)

    def process_post(self):
        return Response().status(Response.Status.METHOD_NOT_ALLOWED)

    def render_html(self, res):
        values = self.build_values(res)
        template = JINJA_ENVIRONMENT.get_template(res.template())
        self.response.write(template.render(values))

    def render_json(self, res):
        values = self.build_values(res)
        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(json.dumps(values))

    def build_values(self, res):
        values = {'_s': self.session()}
        values.update(self.global_values())
        values.update(res.values())
        return values

    def redirect(self, res):
        self.response.headers['Location'] = res.location()

    def registry(self, key = None, value = None):
        if key is None:
            return self.request.registry
        if value is None:
            if isinstance(key, dict):
                for k, v in key.items():
                    self.request.registry[k] = v
                return self
            return self.request.registry[key]
        self.request.registry[key] = value
        return self

    def cookie(self, key, value = None, expires = datetime.timedelta(seconds=0)):
        if value is None:
            return self.request.cookies.get('s')
        self.response.set_cookie(key, value, expires = datetime.datetime.now() + expires, path='/', domain=self.request.host.split(':')[0])
        return self

    def session_class(self):
        return Session

    def session(self):
        cls = self.session_class()
        registry = self.registry()
        if 'session' not in registry:
            self.registry('session', cls(self.cookie('s')))
        return self.registry('session')

    def save_session(self, expires = datetime.timedelta(weeks=12)):
        session = self.session()
        session.csrf_token = str(uuid.uuid4())[:8]
        self.cookie('s', session.encode(), expires)

    def global_values(self, key = None, value = None):
        if key is None:
            registry = self.registry()
            if 'global' not in registry:
                registry['global'] = {}
            return self.registry('global')
        if value is None:
            return self.global_values()[key]
        self.global_values()[key] = value

class AuthHandler(BaseHandler):
    def get(self):
        self.before_get()
        session = self.session()
        if hasattr(session, 'user_base'):
            res = self.process_get()
        else:
            res = Response().redirect_temporarily('/login/?dest=' + urllib.quote_plus(self.request.path_qs))
        self._process(res)
        self.after_get()

    def post(self):
        if self.has_invalid_csrf_token():
            self._process(Response().status(Response.Status.BAD_REQUEST))
            return
        self.before_post()
        session = self.session()
        if hasattr(session, 'user_base'):
            res = self.process_post()
        else:
            res = Response().redirect_temporarily('/login/?dest=' + urllib.quote_plus('/'))
        self._process(res)
        self.after_post()

    def user_base_key(self):
        return ndb.Key(urlsafe=self.session().user_base['key'])

class OauthHandler(BaseHandler):
    def get_flow(self, provider):
        if provider not in OAUTH_PROVIDERS:
            webapp2.abort(Response.Status.BAD_REQUEST)
            return
        if provider not in config.OAUTH:
            webapp2.abort(Response.Status.BAD_REQUEST)
            return
        conf = config.OAUTH[provider]
        provider = OAUTH_PROVIDERS[provider]
        return OAuth2WebServerFlow(
            client_id = conf['client_id'],
            client_secret = conf['client_secret'],
            scope = provider['scope'],
            redirect_uri = self.request.host_url + '/oauth/return/')

class OauthLoginHandler(OauthHandler):
    def process_get(self):
        provider = self.request.get('provider')
        if not provider:
            webapp2.abort(Response.Status.BAD_REQUEST)
            return
        session = self.session()
        session.dest = self.request.get('dest')
        session.provider = provider
        flow = self.get_flow(provider)
        return Response().redirect_temporarily(flow.step1_get_authorize_url())

class OauthReturnHandler(OauthHandler):
    def process_get(self):
        code = self.request.get('code')
        if not code:
            webapp2.abort(Response.Status.BAD_REQUEST)
            return
        session = self.session()
        provider = session.provider
        flow = self.get_flow(provider)
        credentials = flow.step2_exchange(code)
        http = httplib2.Http()
        http = credentials.authorize(http)

        resp, content = http.request(OAUTH_PROVIDERS[provider]['userinfo_uri'], 'GET')
        if int(resp['status']) != Response.Status.OK:
            webapp2.abort(Response.Status.BAD_REQUEST)
            return
        invoker = getattr(self, 'handle_{}'.format(provider))
        result = invoker(resp, content)
        oauth_token = model.OauthToken.find(provider, result['id'])
        if oauth_token:
            user_base = oauth_token.user_base()
        else:
            user_base = model.UserBase.init(provider, result, credentials.access_token)
        session.user_base = user_base.to_dict()

        dest = session.dest if session.dest else '/'
        if type(dest) == unicode:
            dest = str(dest)
        del session.provider
        del session.dest
        return Response().redirect_temporarily(self.request.host_url + dest)

    def handle_google(self, resp, content):
        dict = json.loads(content)
        return {
            'id': dict['id'],
            'name': dict['name']
        }

class LogoutHandler(BaseHandler):
    def process_get(self):
        cls = self.session_class()
        session = cls()
        self.registry('session', session)
        return Response().redirect_temporarily('/')
