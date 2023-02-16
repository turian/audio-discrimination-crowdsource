from django.core.management.utils import get_random_secret_key
from dotenv import dotenv_values

# Load the template and get the placeholders
template = dotenv_values('.env.tmpl')
# Replace the placeholders with actual values
actual = {}
actual['DEBUG'] = True

for key, value in template.items():
    if key == 'SECRET_KEY':
        actual[key] = get_random_secret_key()
    
# Write the actual values to a .env file
with open('.env', 'w') as f:
    for key, value in actual.items():
        
        f.write(f'{key}={value}\n')
