# -*- coding: utf-8 -*-
"""
Cron script.
"""
import urllib

from presence_analyzer.main import app


def fetch_users_data():
    """
    Fetch data users from service.
    """
    data = urllib.urlopen(app.config['USERS_URL'])
    with open(app.config['DATA_XML'], 'wb') as xml_file:
        xml_file.write(data.read())
