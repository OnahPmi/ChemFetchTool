import streamlit as st
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import pandas as pd

def getPropertiesFromPubchem(name, prop):
    # retry mechanism
    session = requests.Session()
    retries = Retry(total=5, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])
    session.mount('https://', HTTPAdapter(max_retries=retries))
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{name}/property/{prop}/txt"
    response = session.get(url, timeout=10)
    status = response.status_code
    if status == 200:
        return response.text.strip()
    else:
        return "Not Found"