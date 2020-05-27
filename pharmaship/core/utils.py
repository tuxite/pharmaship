# -*- coding: utf-8; -*-
"""Core utilities functions."""
# import xml.dom.minidom
import logging
import coloredlogs

import calendar
import datetime

from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.db import connections, reset_queries

from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


# ---------------------------------------------------------------------------#
# Configure the client logging
# ---------------------------------------------------------------------------#
# Logger
log = logging.getLogger("pharmaship")

# logging.basicConfig(
#     handlers=[
#             logging.FileHandler("pharmaship.log"),
#             logging.StreamHandler()
#         ]
#     )
# Handlers
# c_handler = logging.StreamHandler()
f_handler = logging.FileHandler(settings.PHARMASHIP_LOG)
f_handler.setLevel(logging.INFO)

# Create formatters and add it to handlers
# c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# c_handler.setFormatter(c_format)
f_handler.setFormatter(f_format)

# Add handlers to the logger
# log.addHandler(c_handler)
log.addHandler(f_handler)

# log = logging.getLogger("pharmaship")
if settings.DEBUG:
    coloredlogs.install(level='DEBUG', logger=log)
else:
    coloredlogs.install(level='INFO', logger=log)


# For debug only
def query_count_all(show=False) -> None:
    """Print the number of DB queries done since its last call.

    `show`: if True, logs the full SQL queries.
    """
    result = sum(len(c.queries) for c in connections.all())
    log.debug("Queries: %s", result)

    if show:
        for c in connections.all():
            for query in c.queries:
                log.debug(query)
    reset_queries()


# def iso_string_to_date(string):
#     """Convert an ISO 8601 format string to a datetime.datetime object.
#
#     :param string: Date string to convert.
#     :type string: string
#
#     :return: Corresponding datetime.datetime object.
#     :rtype: datetime.datetime
#     """
#     return datetime.datetime.strptime(string, '%Y-%m-%dT%H:%M:%S')


# def remove_xml_pk(xml_string):
#     """Remove the PK attributes to the serialized objects. XML Version.
#
#     This allows to import different alllowances with for instance the
#     same molecules without generating conflicts of primary key.
#     """
#     dom = xml.dom.minidom.parseString(xml_string)
#     for node in dom.getElementsByTagName('object'):
#         if node.hasAttribute("pk"):
#             node.removeAttribute("pk")
#     return dom.toxml("utf-8")


def remove_yaml_pk(yaml_string):
    """Remove the PK attributes to the serialized objects. YAML Version.

    This allows to import different alllowances with for instance the
    same molecules without generating conflicts of primary key.
    """
    data = load(yaml_string, Loader=Loader)
    for item in data:
        item.pop('pk', None)

    output = dump(data, Dumper=Dumper)
    return output


def add_months(sourcedate: datetime.date, months: int) -> datetime.date:
    """Add n calendar months to a date.

    Only add n-months to a date without changing the day.

    :param: sourcedate: A datetime.date instance
    :param: months: number of months to add to sourcedate.
    :type: sourcedate: datetime.date
    :type: months: int

    :return: A datetime.date increased by n months.
    :rtype: datetime.date

    :Example:

    >>> add_months(datetime.date(2020, 1, 31), 3)
    datetime.date(2020, 4, 30)
    """
    # From: https://stackoverflow.com/questions/4130922/how-to-increment-
    # datetime-by-custom-months-in-python-without-using-library
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month // 12
    month = month % 12 + 1
    day = min(sourcedate.day, calendar.monthrange(year, month)[1])
    return datetime.date(year, month, day)


def end_of_month(date_obj):
    """Return the end of month date.

    The returned date corresponds to the last day of the date_obj's month.

    :param: date_obj: A datetime.date instance.
    :type: date_obj: datetime.date

    :return: The corresponding end-of-month date.
    :rtype: datetime.date

    :Example:

    >>> end_of_month(datetime.date(2020, 1, 13))
    datetime.date(2020, 1, 31)
    """
    year = date_obj.year
    month = date_obj.month
    day = calendar.monthrange(year, month)[1]

    return datetime.date(year=year, month=month, day=day)


def get_content_types(app_label="inventory"):
    """Return the dict of content_types id for selected `app_label`.

    :param: app_label: Application name to get content_types for. \
    Default: "inventory"
    :type: app_label: string

    :return: dictionary with model names as keys and related content_type ID \
    as values.
    :rtype: dict

    :Example:

    >>> get_content_types()
    {'allowance': 7, 'article': 25, 'equipment': 8, 'equipmentgroup': 24,
    'equipmentreqqty': 23, 'firstaidkit': 9, 'firstaidkititem': 22,
    'firstaidkitreqqty': 21, 'laboratoryreqqty': 20, 'location': 10,
    'medicine': 19, 'molecule': 11, 'moleculegroup': 18, 'moleculereqqty': 17,
    'qtytransaction': 16, 'rescuebag': 15, 'rescuebagreqqty': 14, 'tag': 13,
    'telemedicalreqqty': 12}

    """
    content_types = {}
    for item in ContentType.objects.filter(app_label=app_label):
        content_types[item.model] = item.id

    return content_types
