from google.appengine.ext import ndb
from google.appengine.api import memcache

class CacheKey:
    def __init__(self, key):
        self.key = key

    def to_str(self):
        return self.key.urlsafe()

    def query(self):
        urlsafe_key = self.to_str()
        key = ndb.Key(urlsafe=urlsafe_key)
        return key.get()

    def get(self):
        model = memcache.get(self.to_str())
        if model:
            return model
        model = self.query()
        model.cache()
        return model

class CachableModel(ndb.Model):
    def cache_key(self):
        return CacheKey(self.key)

    def cache(self):
        self.delete_cache()
        memcache.add(self.cache_key().to_str(), self)

    def put_and_cache(self):
        self.put()
        self.cache()

    def delete_cache(self):
        memcache.delete(self.cache_key().to_str())

class OauthToken(ndb.Model):
    @staticmethod
    def find(provider, provider_id):
        results = OauthToken.query(OauthToken.provider == provider, OauthToken.provider_id == provider_id).fetch()
        if len(results) == 0:
            return None
        return results[0]

    provider = ndb.StringProperty()
    provider_id = ndb.StringProperty()
    token = ndb.StringProperty()

    def user_base(self):
        return self.key.parent().get()

class UserBase(ndb.Model):
    @staticmethod
    def init(provider, result, token):
        user_base = UserBase()
        user_base.name = result['name']
        parent_key = user_base.put()
        oauth_token = OauthToken(parent=parent_key)
        oauth_token.provider = provider
        oauth_token.provider_id = result['id']
        oauth_token.token = token
        oauth_token.put()
        return user_base

    name = ndb.StringProperty()
    def to_dict(self):
        return {
            'key': self.key.urlsafe(),
            'name': self.name
        }