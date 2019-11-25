# fidelis/auth.py

from requests.auth import AuthBase

class FidelisAuth(AuthBase):

    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers['Authorization'] = "bearer " + self.token
        return r