# -*- coding: utf-8; -*-
"""Core configuration functions."""
import json

import yaml
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

try:
    from yaml import CDumper as Dumper
except ImportError:
    from yaml import Dumper

from munch import Munch

from django.conf import settings
from cerberus import Validator

from pharmaship.core.utils import log


def load_config(content, schema):
    """Load the configuration from a YAML file.

    :param content: string containing YAML data (from a config file)
    :param schema: schema filename, not path for validating the content
    :type content: string or bytes
    :type schema: string or Path

    :return: validated config dictionary or False
    :rtype: dict or boolean

    :Example:

    >>> load_config(my_content, "config.json")
    """
    try:
        # config = json.loads(content)
        config = yaml.load(content, Loader=Loader)
    except (ValueError, TypeError, yaml.YAMLError) as error:
        log.error("Unable to parse the config file. %s", error)
        return False

    # Load the schema
    try:
        with open(settings.VALIDATOR_PATH / schema, "r") as fd:
            raw_schema = fd.read()
            fd.close()
    except IOError as error:
        log.error("Unable to read the schema file. %s", error)
        return False

    try:
        schema = json.loads(raw_schema)
    except (ValueError, TypeError) as error:
        log.error("Unable to parse the schema file. %s", error)
        return False

    # Validate the configuration json string
    validator = Validator(schema)

    if validator.validate(config):
        return config
    else:
        log.error("Configuration file not validated. %s", validator.errors)
        return False


def read_config():
    """Read Pharmaship configuration file.

    Read the configuration from yaml source file, validate it against
    a schema and then convert it to Munch instance.

    :return: validated config Munch instance or False
    :rtype: Munch or boolean

    :Example:

    >>> read_config()
    """
    filename = settings.PHARMASHIP_CONF

    try:
        with open(filename, "r") as fdesc:
            content = fdesc.read()
    except IOError as error:
        log.exception("Config file not readable: %s. %s", filename, error)
        return False

    raw_config = load_config(content, "config.json")
    if not raw_config:
        return False

    # Transform dict in pseudo namedtuple recursively
    config = Munch.fromDict(raw_config)

    return config


def write_config(data):
    """Write Pharmaship configuration file.

    :param data: Data to write into the configuration file.
    :type data: Munch instance

    :return: True is written with success.
    :rtype: boolean

    :Example:

    >>> write_config(my_data)
    """
    filename = settings.PHARMASHIP_CONF

    try:
        dict_data = data.toDict()
    except AttributeError as error:
        log.exception("Data is not a Munch instance: %s", error)
        return False

    content = yaml.dump(dict_data, Dumper=Dumper, indent=2)

    try:
        with open(filename, "w") as fdesc:
            fdesc.write(content)
    except IOError as error:
        log.exception("Config file not writable: %s. %s", filename, error)
        return False

    return True
