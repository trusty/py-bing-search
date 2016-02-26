import requests
import threading

def get_requests_session():
    """Returns a new (or existing) requests.Session object for current thread"""

    try:
        ret = get_requests_session.tld.requests_session
    except AttributeError:
        ret = get_requests_session.tld.requests_session = requests.Session()
    return ret
get_requests_session.tld = threading.local()
