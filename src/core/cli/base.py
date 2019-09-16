import typing as t

import asyncio
import abc
import argparse

from conf import settings
from core.cli import commands
from core.utils import import_string


class BaseAppCommand(abc.ABC):
    """The interface for construction of CLI"""

    @property
    @abc.abstractmethod
    def name(self):
        """
        The name in CLI by which this this handler will be launched.
        For example. the name is "run". A handler will start as follows:

            python app.py run

        """

        pass

    @property
    @abc.abstractmethod
    def help(self):
        """
        The help for a command which displayed
        when will be called python app.py COMMAND_NAME --help.
        """

        pass

    def add_arguments(self, parser: argparse.ArgumentParser):
        """
        Adds arguments to the argument parser class for current command.
        The parser it's ArgumentParser class from argparse library.

        For example:
            parser.add_argument('--port', nargs='?', type=int, default=8000)

        """

        pass

    @abc.abstractmethod
    async def handle(self, parsed_args: argparse.Namespace):
        """
        Contains the script for handling of a command.
        """

        pass


def collect_command_classes() -> t.List[t.Type[BaseAppCommand]]:
    """
    Collects, imports and returns command classes
    contained in CLI_COMMAND_CLASSES setting and
    appends commands from src.core.cli.commands.
    """

    command_import_strings = settings.CLI_COMMAND_CLASSES + commands.command_classes
    command_classes = [import_string(c) for c in command_import_strings]

    return command_classes


def execute_cli() -> None:
    """
    The entry point for building of CLI and running it.
    """

    command_classes = collect_command_classes()
    parser = argparse.ArgumentParser()
    sub_parser = parser.add_subparsers(dest='command')
    handlers_map = {}

    for command_class in command_classes:
        command = command_class()
        handlers_map[command.name] = command.handle
        command_parser = sub_parser.add_parser(command.name, help=command.help)
        command.add_arguments(command_parser)

    parsed_args = parser.parse_args()
    handler_func = handlers_map[parsed_args.command]

    if parsed_args.command == 'run':
        handler_func(parsed_args)
    else:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(handler_func(parsed_args))

