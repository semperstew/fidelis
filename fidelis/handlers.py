# fidelis/hooks.py

import fidelis.exceptions

def check_for_other_errors(resp):
    resp.raise_for_status()

def check_for_token_errors(resp):
    if resp.status_code == 400:
        if resp.reason == "Authentication token has expired.":
            raise fidelis.exceptions.ExpiredTokenException
        if resp.reason == "Authentication token is invalid.":
            raise fidelis.exceptions.InvalidTokenException
        
BUILTIN_HANDLERS = [
    check_for_token_errors,
    check_for_other_errors
]