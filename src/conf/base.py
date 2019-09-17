import os


PROJECT_ROOT = os.path.abspath(os.path.join(__file__, '..', '..'))

SECRET_KEY = os.getenv('SECRET_KEY', '')

MONGO_URL = os.getenv('MONGO_URL')

URLS = [
    'apps.messages.urls',
    'apps.users.urls',
    'apps.other.urls',
]

CLI_COMMAND_CLASSES = [
    'scripts.populate_db.PopulateDBAppCommand',
]


MESSAGES_COLLECTION = 'messages'
USERS_COLLECTION = 'users'
ACCESS_TOKEN_COLLECTION = 'access_tokens'

JWT_EXP_SECONDS = 24*60*60  # one day

API_SPECIFICATION_PATH = os.path.join(PROJECT_ROOT, '..', 'docs', 'api.yaml')

CORS_ALLOWED_METHODS = '*'
CORS_ALLOWED_HEADERS = '*'
CORS_ALLOWED_CREDENTIALS = True
CORS_EXPOSED_HEADERS = '*'
CORS_ALLOWED_ORIGINS = [
    'http://0.0.0.0:8001',
]
