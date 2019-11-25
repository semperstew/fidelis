# fidelis/endpoint.py

import requests
import json
import datetime

from urllib.parse import quote, unquote, urlencode

from fidelis import handlers
from fidelis.auth import FidelisAuth
from fidelis.exceptions import TokenException


class FidelisEndpoint(object):

    def __init__(self, host, username, password, 
                 session=None, ignoressl=False):
        self._host = host
        self.baseURL = "https://{}/endpoint/api/".format(self._host)
        self._username = username
        self._password = password
        self._ignoressl = ignoressl
        self._headers = {"Content-Type": "application/json;charset=UTF-8"}
        self._session = session or self._create_new_session()
        self._register_builtin_handlers()


    @property
    def host(self):
        return self._host

    @host.setter
    def host(self, value):
        self._host = value

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, value):
        self._username = value

    @property
    def password(self):
        raise NotImplementedError(
            "Viewing the session password is not allowed.")

    @password.setter
    def password(self, value):
        self._password = value
    
    @property
    def ignoressl(self):
        return self._ignoressl

    @ignoressl.setter
    def ignoressl(self, value):
        self._ignoressl = value

    @property
    def token(self):
        return self._token

    @token.setter
    def token(self, value):
        self._token = value

    def _create_new_session(self):
        session = requests.Session()
        session.headers = self._headers
        session.auth = FidelisAuth(self._get_bearer_token())
        return session

    def _register_builtin_handlers(self):
        for handler in handlers.BUILTIN_HANDLERS:
            self._session.hooks['request'].append(handler)
        self._session.hooks['request'].append(self._after_request)

    def _before_request(self):
        raise NotImplementedError("before_request method not yet implemented")

    def _after_request(self, resp):
        token = resp.headers['Fidelis-Endpoint-Token']
        self._session.auth = FidelisAuth(token)

    def _get_bearer_token(self):
        headers = {"Content-Type": "application/json;charset=UTF-8"}
        body = {"username": self.username, "password": self._password}
        url = self.baseURL + "authenticate"
        r = requests.post(url=url, headers=headers, json=body)
        return r.data['token']

    def __generic_post_request__(self, api, params):
        params = sanitize_params(params)
        url = self.baseURL + api
        try:
            r = self._session.post(url=url, headers=self._headers, json=params)
            return r
        except TokenException:
            self._session.auth = FidelisAuth(self._get_bearer_token())
            r = self._session.post(url=url, headers=self._headers, json=params)
            

def sanitize_params(params):
    return {k:v for k,v in params.items() if v is not None}

def foo(a,b,c,d):
    params = sanitize_params(locals())
    return params

if __name__ == "__main__":
    params = {'a': 1, 'b': None, 'c': 3, 'd': None}
    sanitized_params = foo(**params)
    print(sanitized_params)

