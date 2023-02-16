from django.core.management.utils import get_random_secret_key
from dotenv import dotenv_values


class EnvironmentVarSetting:
    def __init__(self) -> None:
        pass

    def execute(self):
        # Load the template and get the placeholders
        template = dotenv_values(".env.tmpl")
        # Replace the placeholders with actual values
        actual = {}
        actual["DEBUG"] = True
        actual["DEVELOPMENT_MODE"] = "local"
        actual["ALLOWED_HOSTS"] = "localhost 127.0.0.1"

        for key, value in template.items():
            if key == "SECRET_KEY":
                actual[key] = get_random_secret_key()

        # Write the actual values to a .env file
        with open(".env", "w") as f:
            for key, value in actual.items():

                f.write(f"{key}={value}\n")
        return

    def update_env_variable(self, key, value):
        print(key, value)
        # Load the template and get the placeholders
        template = dotenv_values(".env.tmpl")
        # Replace the placeholders with actual values
        actual = {}
        actual["DEBUG"] = True
        actual["DEVELOPMENT_MODE"] = "local"

        for key1, value in template.items():
            if key1 == key:
                # if the key is allowed hosts or trusted origins append to string
                if key == "ALLOWED_HOSTS":
                    actual[key] = "localhost 127.0.0.1 " + value
                else:
                    actual[key1] = value

        print(actual)

        # Write the actual values to a .env file
        with open(".env", "w") as f:
            for key, value in actual.items():
                f.write(f"{key}={value}\n")


EnvironmentVarSetting().execute()
