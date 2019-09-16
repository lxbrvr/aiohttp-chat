import argparse

from motor import motor_asyncio

from conf import settings
from core.cli.base import BaseAppCommand


class CleanDbAppCommand(BaseAppCommand):
    """
    The command for cleaning of mongodb database.
    The database name indicated in MONGO_URL setting.
    """

    name: str = 'clean_db'
    help: str = (
        'Cleans the mongo database based on '
        'MONGO_URL in the project settings.'
    )

    async def handle(self, parsed_args: argparse.Namespace) -> None:
        mongo_client = motor_asyncio.AsyncIOMotorClient(settings.MONGO_URL)
        db_name = mongo_client.get_database().name
        mongo_client.drop_database(db_name)
        mongo_client.close()
