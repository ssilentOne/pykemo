"""
Main module. If pykemo is executed in console, it will lead to this module.
"""

from .general import get_posts, get_creator, Post
from datetime import datetime
from .services import ServiceType
from .core import post, UrlType


def main(*args) -> int:
    "Main function"

    res = post(endpoint="/account/login", url_type=UrlType.SITE,
               json={
                   "username": "EcchiNLGS",
                   "password": "Natca&Gobdak"
               })

    print(res.auth, res.cookies)


    # before = datetime(year=2024, month=6, day=18, hour=23, minute=1)
    # since = datetime(year=2024, month=6, day=18, hour=22)

    # # fumihiko = get_creator("fanbox", "2658856")
    # # kakure_eria = get_creator("discord", "814339508694155294")
    # # deyui = get_creator("patreon", "12733350")
    # dagasi = get_creator("fanbox", "1549213")

    # fancards = dagasi.fancards
    # fanc_file = fancards[0].file
    # fanc_file.save("./downloads/", force=True, verbose=True, server=2)

    # # fumihiko.posts(max_posts=50, before=before, since=since)[0].save("./downloads/*", verbose=True)

    return 0
