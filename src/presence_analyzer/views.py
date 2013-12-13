# -*- coding: utf-8 -*-
"""
Defines views.
"""

import calendar
from flask import redirect, render_template, url_for, make_response, abort
from jinja2 import TemplateNotFound

from presence_analyzer.main import app
from presence_analyzer.utils import (jsonify, get_data, mean,
                                     group_by_weekday,
                                     group_by_weekday_start_end)

import logging
log = logging.getLogger(__name__)  # pylint: disable-msg=C0103


@app.route('/')
@app.route('/<name>')
def mainpage(name=None):
    """
    Redirects to default front page if name equals None or return render
    template from templates directory.
    """
    if not name:
        return redirect(url_for('mainpage', name='presence_weekday.html'))
    try:
        return render_template(name)
    except TemplateNotFound:
        return make_response('Not Found', 404)


@app.route('/api/v1/users', methods=['GET'])
@jsonify
def users_view():
    """
    Users listing for dropdown.
    """
    data = get_data()
    return [{'user_id': i, 'info': data[i]['info']}
            for i in data.keys()]


@app.route('/api/v1/mean_time_weekday/', methods=['GET'])
@app.route('/api/v1/mean_time_weekday/<int:user_id>', methods=['GET'])
@jsonify
def mean_time_weekday_view(user_id=None):
    """
    Returns mean presence time of given user grouped by weekday.
    """
    data = get_data()
    if not user_id:
        raise abort(400)

    if user_id not in data:
        log.debug('User %s not found!', user_id)
        return []

    weekdays = group_by_weekday(data[user_id])
    result = [(calendar.day_abbr[weekday], mean(intervals))
              for weekday, intervals in weekdays.items()]
    return result


@app.route('/api/v1/presence_weekday/', methods=['GET'])
@app.route('/api/v1/presence_weekday/<int:user_id>', methods=['GET'])
@jsonify
def presence_weekday_view(user_id=None):
    """
    Returns total presence time of given user grouped by weekday.
    """
    data = get_data()
    if not user_id:
        raise abort(400)

    if user_id not in data:
        log.debug('User %s not found!', user_id)
        return []

    weekdays = group_by_weekday(data[user_id])
    result = [(calendar.day_abbr[weekday], sum(intervals))
              for weekday, intervals in weekdays.items()]

    result.insert(0, ('Weekday', 'Presence (s)'))
    return result


@app.route('/api/v1/presence_start_end/', methods=['GET'])
@app.route('/api/v1/presence_start_end/<int:user_id>', methods=['GET'])
@jsonify
def presence_start_end_view(user_id=None):
    """
    Returns mean presence time of given user grouped by weekday.
    """
    data = get_data()
    if not user_id:
        raise abort(400)

    if user_id not in data:
        log.debug('User %s not found!', user_id)
        return []

    weekdays = group_by_weekday_start_end(data[user_id])
    result = [(calendar.day_abbr[weekday], value[0], value[1])
              for weekday, value in weekdays.items()]
    return result
