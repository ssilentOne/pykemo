"""
URL types module.
"""

from enum import StrEnum


class UrlType(StrEnum):
    """
    Types of URL endpoints.

    .. note:: The DATA type can be further formatted into different servers. It may not be used as-is.
    """

    SITE = "https://kemono.su"
    "The URL for the Kemono site itself."

    DATA = "https://c{i}.kemono.su"
    "The URL for the backend that stores assets."

    API = "https://kemono.su/api"
    "The URL entrypoint for the Kemono API."

    DISCORD = "https://cdn.discordapp.com"
    "A special URL specifically for Discord assets."
