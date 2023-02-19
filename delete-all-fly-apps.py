#!/usr/bin/env python3

import json
import os
import subprocess


def delete_all():
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


if __name__ == "__main__":
    delete_all()
