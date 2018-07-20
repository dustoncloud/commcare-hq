from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from datetime import timedelta, date

import six
from dateutil.parser import parse as parse_date
from leven import levenshtein


def le_days_diff(max_days, date1, date2):
    """
    Returns True if date1 is less than or equal to max_days away from
    date2, otherwise returns False

    >>> le_days_diff(364, '2018-01-01', '2017-01-20')
    True
    >>> le_days_diff(364, date(2017, 1, 20), date(2018, 1, 1))
    True
    >>> le_days_diff(364, '2018-01-01', '2020-01-20')
    False

    """
    if isinstance(date1, six.string_types):
        date1 = parse_date(date1)
    if isinstance(date2, six.string_types):
        date2 = parse_date(date2)
    return abs(date1 - date2) <= timedelta(max_days)


def le_levenshtein_percent(percent, string1, string2):
    """
    Returns True if Levenshtein distance between string1 and string2,
    divided by max length, is less than or equal to the given percent.

    :param percent: Percent expressed as a decimal between 0 and 1
    :param string1: First string to compare
    :param string2: Second string to compare
    :return: True or False

    >>> le_levenshtein_percent(0.2, 'Riyaz', 'Riaz')
    True
    >>> le_levenshtein_percent(0.2, 'Riyaz', 'Riazz')
    False

    """
    if not 0 <= percent < 1:
        raise ValueError('percent must be greater that or equal to 0 and less than 1')
    distance = levenshtein(string1, string2)
    max_len = max(len(string1), len(string2))
    return distance / max_len <= percent