"""
pykemo entrypoint.
"""

from asyncio import run
from sys import argv

from .main import main

if __name__ == "__main__":
    run(main(*argv))
