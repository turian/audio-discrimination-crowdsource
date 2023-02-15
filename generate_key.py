import secrets
import string
my_key = ''.join(secrets.choice(string.printable) for i in range(60))
# random string will be generated and used as secret key for the app
print(my_key)