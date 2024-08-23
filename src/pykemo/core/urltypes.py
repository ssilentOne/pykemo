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
    DATA = "https://c{i}.kemono.su"
    API = "https://kemono.su/api/v1"
    DISCORD = "https://cdn.discordapp.com" # Specifically for Discord assets
