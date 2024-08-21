"""
Main module. If pykemo is executed in console, it will lead to this module.
"""

from datetime import datetime

from .core import UrlType, get, post
from .general import Post, get_creator, get_creators, get_file_hash, get_posts
from .services import ServiceType


def main(*args) -> int:
    "Main function"

    before = datetime(year=2024, month=6, day=18, hour=23, minute=1)
    since = datetime(year=2024, month=6, day=18, hour=22)

    fumihiko = get_creator("fanbox", "2658856")
    # kakure_eria = get_creator("discord", "814339508694155294")
    # deyui = get_creator("patreon", "12733350")
    # dagasi = get_creator("fanbox", "1549213")

    post = fumihiko.posts(before=before, since=since, max_posts=50)[0]
    print(post)
    # post.save("./downloads/*", verbose=True)

    # channel = kakure_eria.channels[1]
    # msgs = channel.messages(max_msg=150,
    #                         before=datetime(year=2024, month=7, day=21, hour=14),
    #                         since=datetime(year=2024, month=7, day=21, hour=13),
    #                         asynchronous=True)
    # for att in msgs[0].attachments:
    #     att.save("./downloads", verbose=True)

    return 0
