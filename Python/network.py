import re
import json
import requests
from requests.adapters import HTTPAdapter, Retry

URL_REGEX = r"^https?:\/\/((?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b)(?:[-a-zA-Z0-9()@:%_\+.~#?&\/=]*)$"
POST_REQUEST_HEADERS = {
        "Content-Type": "application/json; charset=utf-8",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11"
    }

def is_url_valid(url:str)->bool:
    """
    Check if the URL is valid

    Args:
        url (str): URL

    Returns:
        bool: True if the URL is valid, False otherwise 
    """
    if isinstance(extract_url_domain(url), str):
        return True
    return False

def extract_url_domain(url:str)->bool or str:
    """
    Extract domain from URL

    Args:
        url (str): URL

    Returns:
        bool or str: False if the URL is invalid, domain if the URL is valid
    """
    m = re.search(URL_REGEX, url)
    if m:
        return m.group(1)
    return None

def send_post_request(url:str, payload:str, headers:dict = None)->requests.models.Response:
    """
    Send HTTP POST request

    Args:
        url (str): URL
        payload (str): Payload

    Returns:
        requests.models.Response: Response
    """
    if not is_url_valid(url):
        raise f"Invalid URL <{url}>"
    # decode JSON if the payload is in JSON format
    try:
        payload = json.loads(payload)
    except json.decoder.JSONDecodeError:
        pass
    except Exception as err:
        raise f"{err}"
    # convert to JSON
    payload = json.dumps(payload)
    # start a session
    session = requests.Session()
    # set retry policy
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    # add adapter to session
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    # send request
    response = session.post(url, data=payload, headers=POST_REQUEST_HEADERS if headers is None else headers)
    return response