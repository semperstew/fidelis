# fidelis/utils.py

import datetime
import dateutil.parser

def convert_to_iso8601(value):
  if not isinstance(value, datetime.datetime):
    value = dateutil.parser.parse(value)
  fmt = "%Y-%m-%dT%H:%M:%SZ"
  return datetime.datetime.strftime(value, fmt)