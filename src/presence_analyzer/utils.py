# -*- coding: utf-8 -*-
"""
Helper functions used in views.
"""

import csv
import locale
from json import dumps
from functools import wraps
from datetime import datetime
from lxml import etree
from collections import OrderedDict

from flask import Response

from presence_analyzer.main import app
from presence_analyzer.cache.decorators import cache

import logging
log = logging.getLogger(__name__)  # pylint: disable-msg=C0103


def jsonify(function):
    """
    Creates a response with the JSON representation of wrapped function result.
    """
    @wraps(function)
    def inner(*args, **kwargs):
        return Response(dumps(function(*args, **kwargs)),
                        mimetype='application/json')
    return inner


@cache
def get_data():
    """
    Extracts presence data from CSV file and groups it by user_id.

    It creates structure like this:
    data = {
        'user_id': {
            dates: {
                datetime.date(2013, 10, 1): {
                    'start': datetime.time(9, 0, 0),
                    'end': datetime.time(17, 30, 0),
                },
                datetime.date(2013, 10, 2): {
                    'start': datetime.time(8, 30, 0),
                    'end': datetime.time(16, 45, 0),
                },
            },
            info: {
                'name': 'User 0',
                'avatar': '/api/images/users/0'
            }
        }
    }
    """
    data = {}
    tree = etree.parse(app.config['DATA_XML'])
    server_url = u'%s://%s' % (
        tree.xpath('//intranet/server/protocol')[0].text,
        tree.xpath('//intranet/server/host')[0].text
    )

    xml_data = {
        int(el.attrib['id']): {
            ch.tag: unicode(ch.text) for ch in el.getchildren()
        }
        for el in tree.xpath('//intranet/users/user')
    }

    with open(app.config['DATA_CSV'], 'r') as csvfile:
        presence_reader = csv.reader(csvfile, delimiter=',')
        for i, row in enumerate(presence_reader):
            if len(row) != 4:
                # ignore header and footer lines
                continue

            try:
                user_id = int(row[0])
                date = datetime.strptime(row[1], '%Y-%m-%d').date()
                start = datetime.strptime(row[2], '%H:%M:%S').time()
                end = datetime.strptime(row[3], '%H:%M:%S').time()
            except (ValueError, TypeError):
                log.debug('Problem with line %d: ', i, exc_info=True)

            data.setdefault(user_id, {'dates': {}})['dates'][date] = {
                'start': start, 'end': end
            }

        for user_id in data.keys():
            user_info = xml_data.get(user_id)
            if user_info:
                data[user_id]['info'] = user_info
                data[user_id]['info']['avatar'] = u'%s%s' % (
                    server_url,
                    data[user_id]['info']['avatar']
                )
            else:
                del data[user_id]

    return OrderedDict(sorted(data.iteritems(),
                              key=lambda x: x[1]['info']['name'],
                              cmp=locale.strcoll))


def group_by_weekday(items):
    """
    Groups presence entries by weekday.
    """
    result = {i: [] for i in range(7)}
    for date in items['dates']:
        start = items['dates'][date]['start']
        end = items['dates'][date]['end']
        result[date.weekday()].append(interval(start, end))
    return result


def group_by_weekday_start_end(items):
    """
    Groups presence entries by weekday.
    """
    result = {i: {'start': [], 'end': []} for i in range(7)}

    for date in items['dates']:
        start = items['dates'][date]['start']
        end = items['dates'][date]['end']
        result[date.weekday()]['start'].append(seconds_since_midnight(start))
        result[date.weekday()]['end'].append(seconds_since_midnight(end))

    return {i: [mean(result[i]['start']), mean(result[i]['end'])]
            for i in range(7)}


def seconds_since_midnight(time):
    """
    Calculates amount of seconds since midnight.
    """
    return time.hour * 3600 + time.minute * 60 + time.second


def interval(start, end):
    """
    Calculates inverval in seconds between two datetime.time objects.
    """
    return seconds_since_midnight(end) - seconds_since_midnight(start)


def mean(items):
    """
    Calculates arithmetic mean. Returns zero for empty lists.
    """
    return float(sum(items)) / len(items) if len(items) > 0 else 0.0
