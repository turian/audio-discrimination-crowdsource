import json
import subprocess
import os
from set_env import EnvironmentVarSetting
import sys
from dotenv import dotenv_values

import os
from dotenv import load_dotenv
from pathlib import Path
from django.core.management.utils import get_random_secret_key

BASE_DIR = Path(__file__).resolve()

load_dotenv(".env")


class FlyHelper:
    def __init__(self) -> None:
        pass

    def create_app(self, app_name):
        # Define your app parameters

        region = "iad"  # default to Virginia
        # Database detail
        user = app_name
        password = get_random_secret_key()[0:10]
        host = "audio-discrimination-croudsource-dev-db.internal"
        port = 5432
        db = 5433
        database_url = "postgres://{0}:{1}@{2}:{3}/{4}".format(
            user, password, host, port, db
        )

        command = f'flyctl launch --name {app_name} --region {region} --env "DATABASE_URL={database_url}"'
        process = subprocess.run(command, shell=True, capture_output=True, text=True)

        if process.returncode != 0:
            raise "Error launching Fly app"
        else:
            process = subprocess.run(
                ["flyctl", "status", "--app", app_name, "--json"],
                stdout=subprocess.PIPE,
                text=True,
            )

            # Parse the output as a JSON object
            try:
                info = json.loads(process.stdout)
                hostName = info["Hostname"]
                domain = "https://" + hostName

                EnvironmentVarSetting().update_env_variable(
                    database_url, hostName, domain
                )

            except json.decoder.JSONDecodeError:
                raise f"Error parsing JSON output: {process.stdout}"

    # deploy the app to fly.io
    def deploy(self, app_name=None, mode="staging"):
        # import secret values before deployment
        FlyHelper().import_secrets(mode=mode)

        if app_name is None:
            command = f"fly deploy"
        else:
            command = f"fly deploy --app {app_name}"
        process = subprocess.run(command, shell=True)
        if process.returncode != 0:
            raise "Error Deploying Fly app"

        print("Fly app Deployed successfully")

    # Import secrets to fly.io
    def import_secrets(self, mode="staging"):

        # import secrets to fly.io
        template = dotenv_values(".env.tmpl")

        for key, value in template.items():

            if key == "DEVELOPMENT_MODE":
                command = "flyctl secrets set " + key + "=" + mode
            else:
                command = "flyctl secrets set " + key + "=" + os.getenv(key)
                process = subprocess.run(command, shell=True)

    def open(self, app_name):

        # open app on browser with app_name
        command = "fly open -app {app_name}"
        process = subprocess.run(command, shell=True)


# conditionals to run specific method on bash command run
if sys.argv[1] == "launch":

    FlyHelper().create_app(sys.argv[2])

elif sys.argv[1] == "deploy":

    if len(sys.argv) > 2:
        FlyHelper().deploy(sys.argv[2])
    else:
        FlyHelper().deploy()

elif sys.argv[1] == "open":

    if len(sys.argv) > 2:
        FlyHelper().open(sys.argv[2])

    else:
        FlyHelper().open()

elif sys.argv[1] == "secrets":
    FlyHelper().import_secrets()
