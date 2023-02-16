import json
import subprocess
import os
from set_env import EnvironmentVarSetting
import sys


class FlyHelper:
    def __init__(self) -> None:
        pass

    def create_app(self, app_name):
        print(app_name)
        # Define your app parameters

        region = "iad"  # default to Virginia
        database_url = "postgres://user:password@host:port/database"

        # Launch the Fly app and set the DATABASE_URL environment variable
        # command = f'flyctl launch --name {app_name} --region {region} "'
        command = f'flyctl launch --name {app_name} --region {region} --env "DATABASE_URL={database_url}"'
        print(command)
        process = subprocess.run(command, shell=True, capture_output=True, text=True)

        print("__________________FI____________________")
        print("here")
        print(process.stdout)
        print("________________fo______________________")

        # Check the return code of the Fly CLI command
        if process.returncode != 0:
            print("Error launching Fly app")
        else:
            print("Fly app launched successfully")

            # Get the output of the "info" command as a JSON object
            process = subprocess.run(
                ["flyctl", "status", "--app", app_name, "--json"],
                stdout=subprocess.PIPE,
                text=True,
            )

            # Parse the output as a JSON object
            try:
                info = json.loads(process.stdout)

                print("===")
                print(info)

                print("===++")
                hostName = info["Hostname"]

                print(info["Hostname"])
                domain = "https://" + hostName

                EnvironmentVarSetting().update_env_variable(
                    "DATABASE_URL", database_url
                )
                EnvironmentVarSetting().update_env_variable("ALLOWED_HOSTS", hostName)
                EnvironmentVarSetting().update_env_variable(
                    "CSRF_TRUSTED_ORIGINS", domain
                )

            except json.decoder.JSONDecodeError:
                print(f"Error parsing JSON output: {process.stdout}")
                exit(1)

    # deploy the app to fly.io
    def deploy(self, app_name):

        # import secret values
        FlyHelper().import_secrets()

        command = f'fly deploy --app {app_name}"'
        print(command)
        process = subprocess.run(command, shell=True)
        if process.returncode != 0:
            print("Error Deploying Fly app")
        else:
            print("Fly app Deployed successfully")
            print(process.stderr)

    # Import secrets to fly.io
    def import_secrets(self, app_name):

        command = "flyctl secrets import -a {app_name} < .env"
        process = subprocess.run(command, shell=True)
        return process.returncode != 0

    def open(self, app_name):

        command = "fly open -app {app_name}"
        process = subprocess.run(command, shell=True)
        if process.returncode != 0:
            print("Error Opening your Fly app")
        else:
            print("Your fly app is running")


if sys.argv[1] == "launch":
    FlyHelper().create_app(sys.argv[2])
elif sys.argv[1] == "deploy":
    FlyHelper().deploy(sys.argv[2])
elif sys.argv[1] == "open":
    FlyHelper().open(sys.argv[2])
# command = ['ls', '-l']

# import simplejson

# process = subprocess.run('fly status', stdout=subprocess.PIPE, text=True )
# print('----')
# print(process.stdout)
# dataform = process.stdout.decode('utf-8').replace('\0', '')
# dataform = str(process.stdout).strip("'<>() ").replace('\'', '\"')

# print(dataform)
# print(type(process.stdout))
# info_json = json.loads(dataform)
# print(info_json)
# domains = process.stdout.read().splitlines()
# print(domains)
# flyctl secrets import -a <app-name> < .env
# flyctl ssh console -a <app-name>       - connect to server
