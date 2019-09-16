import importlib
import os


DEFAULT_SETTINGS_MODULE_ENV_NAME = 'SETTINGS_MODULE'


class Settings:
    def __init__(self, settings_module_env_name):
        settings_module_path = os.environ.get(settings_module_env_name, None)

        if not settings_module_path:
            raise RuntimeError(
                'You must define the environment '
                f'variable {settings_module_env_name}.'
            )

        settings_module = importlib.import_module(settings_module_path)

        for setting in dir(settings_module):
            if setting.isupper():
                setattr(self, setting, getattr(settings_module, setting))


settings = Settings(DEFAULT_SETTINGS_MODULE_ENV_NAME)
