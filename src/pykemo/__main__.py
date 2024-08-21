"""
pykemo entrypoint.
"""

from sys import argv

from .main import main

if __name__ == "__main__":
    main(*argv)
