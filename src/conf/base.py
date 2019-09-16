import os


PROJECT_ROOT = os.path.abspath(os.path.join(__file__, '..', '..'))

SECRET_KEY = os.getenv('SECRET_KEY', '')

MONGO_URL = os.getenv('MONGO_URL')

URLS = [
    'apps.messages.urls',
    'apps.users.urls',
]

CLI_COMMAND_CLASSES = [
    'scripts.populate_db.PopulateDBAppCommand',
]


MESSAGES_COLLECTION = 'messages'
USERS_COLLECTION = 'users'
ACCESS_TOKEN_COLLECTION = 'access_tokens'

JWT_EXP_SECONDS = 24*60*60  # one day
