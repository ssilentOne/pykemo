"""
Main module. If pykemo is executed in console, it will lead to this module.
"""

from .general import get_posts, get_creator, Post, get_file_hash, get_creators
from datetime import datetime
from .services import ServiceType
from .core import post, UrlType, get


def main(*args) -> int:
    "Main function"

    print(get_creators())

    # before = datetime(year=2024, month=6, day=18, hour=23, minute=1)
    # since = datetime(year=2024, month=6, day=18, hour=22)

    # fumihiko = get_creator("fanbox", "2658856")
    # kakure_eria = get_creator("discord", "814339508694155294")
    # deyui = get_creator("patreon", "12733350")
    # dagasi = get_creator("fanbox", "1549213")

    # fumihiko.posts(before=before, since=since, max_posts=50)[0].save("./downloads/*", verbose=True)

    # channel = kakure_eria.channels[1]
    # msgs = channel.messages(max_msg=150,
    #                         before=datetime(year=2024, month=7, day=21, hour=14),
    #                         since=datetime(year=2024, month=7, day=21, hour=13),
    #                         asynchronous=True)
    # for att in msgs[0].attachments:
    #     att.save("./downloads", verbose=True)

    return 0
