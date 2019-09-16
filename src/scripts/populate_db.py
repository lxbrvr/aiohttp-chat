import argparse

from motor import motor_asyncio

from apps.messages.models import MessageModel
from apps.messages.query_sets import MessagesQS
from apps.users.models import UserModel
from apps.users.query_sets import UsersQS
from conf import settings
from core.cli.base import BaseAppCommand


class PopulateDBAppCommand(BaseAppCommand):
    name: str= 'populate_db'
    help: str = 'Populates the mongo database with fake data.'

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            '--number_of_users',
            type=int,
            default=10,
            help='Number of users to be created.',
        )
        parser.add_argument(
            '--number_of_messages_per_user',
            type=int,
            default=10,
            help='Number of messages to be created pre user.',
        )

    async def handle(self, parsed_args) -> None:
        mongo_client = motor_asyncio.AsyncIOMotorClient(settings.MONGO_URL)
        db = mongo_client.get_database()
        users, messages = [], []

        for i in range(parsed_args.number_of_users):
            user = UserModel(username=f'username{i}', password='password')
            users.append(user)

            for j in range(parsed_args.number_of_messages_per_user):
                message = MessageModel(text=f'text{j}', author_uuid=user.uuid)
                messages.append(message)

        await UsersQS(db=db).insert_many(users)
        await MessagesQS(db=db).insert_many(messages)

        mongo_client.close()
