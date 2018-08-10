import unittest
import requests
import sys
import json
from datetime import datetime

sys.path.append('../')

from model import *
from conditions import *


URL = 'http://localhost:8080'

SESSION = requests.Session()

def GET(path):
    return SESSION.get(URL + path)


def POST(path, data):
    return SESSION.post(URL + path, data, headers={'Content-Type':'application/json'})


class TestSimpleRequests(unittest.TestCase):

    def test(self):
        r = POST('/meals', Meal(name='luncz').dumps())

