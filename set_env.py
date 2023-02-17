#!/usr/bin/env python3

import os
from django.core.management.utils import get_random_secret_key
from dotenv import dotenv_values, set_key

import click
import re


class EnvironmentVarSetting:
    def __init__(self) -> None:
        pass

    def create(self, handle: str):
        assert not os.path.exists(".env"), "File .env already exists, aborting. Please delete it if you're sure you want to do this."
        values = {
            "DEBUG": True,
            "DEVELOPMENT_MODE": "local",
            "ALLOWED_HOSTS": "localhost 127.0.0.1 [::1]"
            "HANDLE": handle
            "SECRET_KEY": get_random_secret_key(),
        }

        for key, value in values.items():
            set_key(".env", key, value)
        return

    def update_env_variable(self, database_url, host_name, domain):
        # Load the template and get the placeholders

        values = dotenv_values(".env")

        set_key(".env", "DATABASE_URL", database_url)
        set_key(".env", "CSRF_TRUSTED_ORIGINS", domain)
        set_key(".env", "ALLOWED_HOSTS", values["ALLOWED_HOSTS"] + " " + host_name)


def is_valid_flyio_handle(name):
    #pattern = r'^[a-z0-9]([a-z0-9\-]{1,61}[a-z0-9])?$'
    pattern = r'^[a-z0-9]([a-z0-9\-]{1,24}[a-z0-9])?$'
    return bool(re.match(pattern, name))

@click.command()
@click.argument('handle')
def execute(handle):
    assert is_valid_flyio_handle(handle), "Invalid handle"
    EnvironmentVarSetting().execute(handle)


if __name__ == "__main__":
    execute()