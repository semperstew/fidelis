# fidelis/credentials.py

import datetime
import requests
import threading
from dateutil.tz import tzlocal
from collections import namedtuple



def _local_now():
  return datetime.datetime.now(tzlocal())

class FidelisCredentials(object):
  """Object to hold authentication credentials"""

  _default_token_timeout = 10 * 60

  def __init__(self, username, password, baseURL, token=None, ignoressl=False):
    self.baseURL = baseURL
    self._username = username
    self._password = password
    self._token = token
    self._ignoressl = ignoressl
    self._time_fetcher = _local_now
    self._expiration = self._time_fetcher()
    self._refresh_lock = threading.Lock()
    self.refresh()
    
  @property
  def token(self):
      return self._token

  @token.setter
  def token(self, value):
      self._token = value
    
  @baseURL
  def baseURL(self):
    return self.baseURL

  @baseURL.setter
  def baseURL(self, value):
    self.baseURL = value
    self._update_expiration()

  def _refresh_needed(self, refresh_in=None):
    """Check if a token refresh is needed."""
    if self._expiration is None:
      return False
    
    if refresh_in is None:
      refresh_in = self._default_token_timeout

    if self._seconds_remaining() >= refresh_in:
      return False

    return True
    
  def _is_expired(self):
    """Check if token is expired"""
    return self._refresh_needed(refresh_in=0)

  def refresh(self, new_token=None):
    if new_token is not None:
      self._token = new_token
      self._update_expiration()

    if not self._is_expired():
      return
    else:
      with self._refresh_lock:
        self._protected_refresh()

  def _protected_refresh(self):
    """Refresh bearer token"""
    url= self.baseURL + 'authenticate'
    body={'username': self._username, 'password': self._password}
    headers={'Content-Type':'application/json'}
    verify=self._ignoressl
    r = requests.post(url=url, headers=headers, json=body, verify=verify)
    self._token = r.data['token']
    self._update_expiration()

  def _seconds_remaining(self):
    """Calculate remaining seconds until token expiration"""
    delta = self._expiration - self._time_fetcher()
    return delta.total_seconds()

  def _update_expiration(self):
    delta = datetime.timedelta(seconds=self._default_token_timeout)
    self._expiration = self._time_fetcher() + delta

  def __call__(self, r):
    self.refresh()
    r.headers['Authorization'] = "bearer " + self._token
    return r

