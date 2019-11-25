# fidelis/endpoint.py

import requests
import json
import datetime

from urllib.parse import quote, unquote, urlencode

from fidelis import handlers
from fidelis.credentials import FidelisCredentials
from fidelis.exceptions import TokenException
from fidelis.utils import convert_to_iso8601


class FidelisEndpoint(object):

    _default_token_expiration = 10 * 60

    def __init__(self, host, username, password, 
                 session=None, ignoressl=False):
        self._host = host
        self.baseURL = "https://{}/endpoint/api/".format(self._host)
        self.creds = FidelisCredentials(username=username, 
                                        password=password,
                                        baseURL=self.baseURL, 
                                        ignoressl=ignoressl)
        self._ignoressl = ignoressl
        self._headers = {"Content-Type": "application/json"}
        self._session = session or self._create_new_session()
        self._register_request_handlers()


    @property
    def host(self):
        return self._host

    @host.setter
    def host(self, value):
        self._host = value
        self.baseURL = "https://{}/endpoint/api/".format(self._host)
        self.creds.baseURL = self.baseURL
    
    @property
    def ignoressl(self):
        return self._ignoressl

    @ignoressl.setter
    def ignoressl(self, value):
        self._ignoressl = value

    def _create_new_session(self):
        session = requests.Session()
        session.headers = self._headers
        session.auth = self.creds
        return session

    def _register_request_handlers(self):
        for handler in handlers.BUILTIN_HANDLERS:
            self._session.hooks['request'].append(handler)
        self._session.hooks['request'].append(self._after_request)

    def _before_request(self):
        raise NotImplementedError("before_request method not yet implemented")

    def _after_request(self, resp):
        token = resp.headers['Fidelis-Endpoint-Token']
        self._session.auth.refresh(token)

    def _get_token(self):
        return self.creds.token

    def __genericPOST__(self, api, **kwargs):
        url = self.baseURL + api
        params = sanitize_params(kwargs)
        return self._session.post(url=url, headers=self._headers, json=params)
            
    def __genericGET__(self, api, **kwargs):
        url = self.baseURL + api
        params = sanitize_params(kwargs)
        return self._session.get(url=url, headers=self._headers, json=params)

    def get_alert_rules(self, limit, offset, sort, search):
        """
        View alert rules
        
        Arguments:
            limit {int} -- Limits the number of alert rules returned. 
            Defaults to 50
            offset {int} -- Index of the starting row returned. 
            Defaults to 0.
            sort {str} -- Sorts the result before applying limit and offset.
            Defaults to `CreatedDate`.
            search {dict} -- A filter applied on results of the get operation.
            See Search Parameter Examples in the Fidelis API Documentation.
        """
        return self.__genericGET__(api='alertrules', **locals())

    def create_alert_rule(self, name, rulesJSON, alertSeverity, 
                          maxHitsAllowed, doNotAlert):
        """
        Create a new alert rule. NOT IMPLEMENTED
        
        Arguments:
            name {str} -- Name to assign to new rule.
            rulesJSON {dict} -- Dictionary object defining the new rule.
            alertSeverity {int} -- Relative severity to assign to new rule. 
            Defaults to `3`.
            maxHitsAllowed {int} -- Maximum number of times the new rule 
            triggers, after which the alert rule is not executed. Defaults to 
            `1`. A value of 0 means the maximum number of hits is infinity.
            doNotAlert {boolean} -- Only perform rule actions but do not create
            an alert record when the alert rule triggers. Defaults to `False`.
        """
        raise NotImplementedError(
            "`create_alert_rule()` method not yet implemented.")
    
    def delete_alert_rule(self, alertRuleIds):
        """
        Delete one or more alert rules. NOT IMPLEMENTED
        
        Arguments:
            alertRuleIds {list} -- list of alert rule ID strings
        """
        raise NotImplementedError(
        "`delete_alert_rule` method not yet implemented.")

    def get_alerts(self, skip, take, sort, facetSearch, startDate, endDate):
        """
        Get alert records.
        
        Arguments:
            skip {int} -- Index of the starting row returned. Defaults to `0`.
            take {int} -- Limits the number of alerts returned. Defaults to 
            all.
            sort {str} -- Sorts the result before applying `take` and `skip`.
            Defaults to `CreatedDateDescending`.
            facetSearch {str} -- A filter applied on the results. Defaults
            to empty string.
            startDate {datetime.datetime} -- The start of the time range of 
            returned values.
            endDate {datetime.datetime} -- The end of the time range of 
            returned values.

            Note: `startDate` and `endDate` times apply to the server and are
            converted to UTC format in the query.
        """
        startDate = convert_to_iso8601(startDate)
        endDate = convert_to_iso8601(endDate)
        return self.__genericGET__(api='alerts/getalerts', **locals())

    
def sanitize_params(params):
    return {k:v for k,v in params.items() if v is not None}

def construct_search_dict(d):
    searchfields = []
    for fieldname, value in d.items():
        if hasattr(value, '__iter__'):
            values = [{'value':v} for v in value]
        else:
            values = [{'value': value}]
        searchfields.append({'fieldName':fieldname, 'values':values})
    return {'searchFields': searchfields}
    