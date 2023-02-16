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

    def update_env_variable(self, database_url, hostName, domain):
        print(database_url, hostName, domain)
        # Load the template and get the placeholders

        ll = {
            "DEBUG": True,
            "DEVELOPMENT_MODE": "local",
            "ALLOWED_HOSTS": "localhost 127.0.0.1  [::1] " + hostName,
            "DATABASE_URL": database_url,
            "SECRET_KEY": get_random_secret_key(),
            "CSRF_TRUSTED_ORIGINS": domain,
        }
        # Write the actual values to a .env file
        with open(".env", "w") as f:
            print("writting")
            for key, value in ll.items():
                print(key, value)
                f.write(f"{key}={value}\n")


# EnvironmentVarSetting().execute()
