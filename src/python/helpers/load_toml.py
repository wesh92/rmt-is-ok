from tomli import load
import os


def load_toml(absolute_path: str = None):
    # define the absolute path to the config file
    if absolute_path is None:
        full_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', 'configs', 'use.toml'))
    else:
        full_path = absolute_path
    # open the config file and return the data
    with open(full_path, mode="rb") as f:
        return load(f)


def currency_mapping():
    CONFIG = load_toml().get('currencies')
    return {x['id']: x['currency'] for x in CONFIG}
