#!/usr/bin/env python3

import shlex
import subprocess

import json
import os
import string
import subprocess
from pathlib import Path
import random

import click
from dotenv import dotenv_values

BASE_DIR = Path(__file__).resolve()

from set_env import EnvironmentVarSetting


def postgres_password() -> str:
    # Define the length of the password
    password_length = 16
    # Define the character set
    characters = string.ascii_letters + string.digits
    # Generate the password
    password = "".join(random.choice(characters) for i in range(password_length))
    return password


def run_to_popen(cmd):
    # print(repr(cmd))
    # Split the command string into a list of its components
    cmd_list = shlex.split(cmd)
    # Create a list that can be used as the argument to Popen
    popen_list = [arg for arg in cmd_list]
    ## Add the stdout and stderr parameters
    # popen_list.extend([subprocess.PIPE, subprocess.PIPE])
    # Return the list
    return popen_list


def run_command(cmd, stdin=None):
    print(cmd)
    cmd = run_to_popen(cmd)
    # print(cmd)
    if not stdin:
        proc = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
    else:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
            text=True,
        )
        # proc.stdin.write(stdin.encode())
        proc.stdin.write(stdin)
        proc.stdin.close()
    while True:
        # Read a line from the stdout pipe, if there is one
        stdout_line = proc.stdout.readline().strip()
        if stdout_line:
            print(stdout_line)

        # Read a line from the stderr pipe, if there is one
        stderr_line = proc.stderr.readline().strip()
        if stderr_line:
            print(stderr_line)

        # Check if the process has completed
        if proc.poll() is not None:
            break

    return proc.returncode


class FlyHelper:
    def __init__(self) -> None:
        # Read dotenv to a dict
        self.app_name = dotenv_values(".env")["APP_NAME"]
        pass

    # I wasn't able to get any of this to work because it doesn't allow me to pass
    # the interactive information about the postgres database, and we need that.
    #    def launch_app(self):
    #        # Define your app parameters
    #
    #        region = "iad"  # default to Virginia
    #
    #        """
    #        # Database detail
    #        user = "postgres"
    #        password = postgres_password()
    #        host = f"{self.app_name}-db.internal"
    #        port = 5432
    #
    #        database_url = "postgres://{0}:{1}@{2}:{3}".format(user, password, host, port)
    #        """
    #        # command = f'flyctl launch --auto-confirm --name {self.app_name} --region {region} --env "DATABASE_URL={database_url}" --dockerfile Dockerfile --dockerignore-from-gitignore'
    #        # command = f'flyctl launch --name {self.app_name} --region {region} --env "DATABASE_URL={database_url}" --dockerfile Dockerfile --dockerignore-from-gitignore'
    #        command = f"flyctl launch --name {self.app_name} --region {region} --dockerfile Dockerfile --dockerignore-from-gitignore"
    #        command = f"flyctl launch --name $APP_NAME --region iad --dockerfile Dockerfile --dockerignore-from-gitignore"
    #        print("Please run this command:\n\n")
    #        print(command)
    #        print("\n\n")
    #        print("And answer the questions as follows:")
    #        print("# Would you like to set up a Postgresql database now? Yes")
    #        print(
    #            "# Select configuration: Development - Single node, 1x shared CPU, 256MB RAM, 1GB disk"
    #        )
    #        print("# Would you like to set up an Upstash Redis database now? No")
    #        print("# Would you like to deploy now? No")
    #        print("\n\n")
    #        print("\n\n")
    #        input = """
    # Y
    #
    # N
    # N
    #        """
    #
    #        # process = subprocess.run(command, shell=True, capture_output=True, text=True, stdin=io.StringIO(input))
    #        returncode = run_command(command, stdin=input)
    #        if returncode != 0:
    #            raise "Error launching Fly app"

    # Better to run this manually to see any errors
    # which otherwise might not get logged
    """
    # deploy the app to fly.io
    def deploy(self):

        command = f"fly deploy --app {self.app_name}"
        returncode = run_command(command)
        if returncode != 0:
            raise Exception("Error Deploying Fly app")

        print("Fly app Deployed successfully")
    """

    # Import secrets to fly.io
    def import_secrets(self):
        self.save_app_hostname_to_env()
        # import secrets to fly.io
        values = dotenv_values(".env")
        for key, value in values.items():
            command = "flyctl secrets set " + key + "=" + repr(value)
            returncode = run_command(command)
            if returncode != 0:
                raise Exception("Error importing secrets to Fly")

    def save_app_hostname_to_env(self):
        process = subprocess.run(
            ["flyctl", "status", "--app", self.app_name, "--json"],
            stdout=subprocess.PIPE,
            text=True,
        )

        # Parse the output as a JSON object
        try:
            info = json.loads(process.stdout)
            print(info)
            host_name = info["Hostname"]
            domain = "https://" + host_name

            EnvironmentVarSetting().update_env_variable(host_name, domain)

        except json.decoder.JSONDecodeError:
            raise Exception(f"Error parsing JSON output: {process.stdout}")

    # Also pointless now that app_name is env variable.
    """
    def open(self):
        # open app on browser with app_name
        command = "fly open -app {self.app_name}"
        process = subprocess.run(command, shell=True)
    """

    def delete_all(self):
        if os.path.exists("fly.toml"):
            os.remove("fly.toml")

        # delete all fly apps
        command = "flyctl apps list --json"
        process = subprocess.run(command, shell=True, capture_output=True, text=True)
        if process.returncode != 0:
            raise Exception("Error listing Fly apps")
        else:
            try:
                info = json.loads(process.stdout)
                for app in info:
                    print(app["Name"])
                    command = f"flyctl destroy {app['Name']} -y"
                    process = subprocess.run(command, shell=True)
                    if process.returncode != 0:
                        raise Exception("Error deleting Fly app")

            except json.decoder.JSONDecodeError:
                raise Exception(f"Error parsing JSON output: {process.stdout}")


@click.command()
@click.argument("command")
def run(command):
    {
        # "launch": FlyHelper().launch_app,
        # "deploy": FlyHelper().deploy,
        "open": FlyHelper().open,
        "import_secrets": FlyHelper().import_secrets,
        # Remove this after dev is done and this PR is ready to merge
        "delete_all": FlyHelper().delete_all,
    }[command]()


if __name__ == "__main__":

    run()
