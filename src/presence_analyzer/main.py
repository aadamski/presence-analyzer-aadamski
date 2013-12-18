# -*- coding: utf-8 -*-
"""
Flask app initialization.
"""
import os.path
from flask import Flask

DATA_DIR = os.path.join(
    os.path.dirname(__file__), '..', '..', 'runtime', 'data'
)

MAIN_DATA_CSV = os.path.join(
    DATA_DIR, 'sample_data.csv'
)

MAIN_USER_XML = os.path.join(
    DATA_DIR, 'users.xml'
)

USERS_URL = 'http://sargo.bolt.stxnext.pl/users.xml'


app = Flask(__name__)  # pylint: disable-msg=C0103
app.config.update(
    DEBUG=True,
    DATA_CSV=MAIN_DATA_CSV,
    DATA_XML=MAIN_USER_XML,
    USERS_URL=USERS_URL
)
