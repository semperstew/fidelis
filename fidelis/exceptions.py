# fidelis/exceptions.py

from requests.exceptions import RequestException

class TokenException(RequestException):
    """A Token error occurred."""

class ExpiredTokenException(TokenException):
    """Authentication token has expired"""

class InvalidTokenException(TokenException):
    """Authentication token is invalid"""

