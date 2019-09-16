import argparse

from core.app import run_app
from core.cli.base import BaseAppCommand


class RunServerAppCommand(BaseAppCommand):
    name: str = 'run'
    help: str = 'Runs the web server.'

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument('--port', nargs='?', type=int, default=8000)

    def handle(self, parsed_args: argparse.Namespace) -> None:
        run_app(port=parsed_args.port)
