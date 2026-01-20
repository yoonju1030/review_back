import os
import json

class Config(object):
    DEBUG = False
    TESTING = False
    # MariaDB Info
    MARIADB_USER = os.environ.get("MARIADB_USER")
    MARIADB_PASSWORD = os.environ.get("MARIADB_PASSWORD")
    MARIADB_DATABASE = os.environ.get("MARIADB_DATABASE")
    MARIADB_HOST = os.environ.get("MARIADB_HOST")
    MARIADB_PORT = os.environ.get("MARIADB_PORT")
    ALLOWED_HOST = os.environ.get("ALLOWED_HOST")

config = {"config": Config}