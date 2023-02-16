
import json
import subprocess
from dotenv import dotenv_values



class FlyHelper: 
    
    def __init__(self) -> None:
        pass
    
    def create_app(self, app_name='audio-discrimination-croudsource-dev'):
        # Define your app parameters
        
        region = 'iad'
        database_url = 'postgres://user:password@host:port/database'

        # Launch the Fly app and set the DATABASE_URL environment variable
        # command = f'flyctl launch --name {app_name} --region {region} "'
        command = f'flyctl launch --name {app_name} --region {region} --env "DATABASE_URL={database_url}"'
        print(command)
        process = subprocess.run(command, shell=True)
        print(process.stdout)
        config_json = json.loads(process.stdout)
        print(config_json)
        
        # Load the template and get the placeholders
        template = dotenv_values('.env.tmpl')
        
        
        

        # Check the return code of the Fly CLI command
        if process.returncode != 0:
            print('Error launching Fly app')
        else:
            print('Fly app launched successfully')

FlyHelper().create_app()




