"""
URL types module.
"""

from enum import StrEnum


class UrlType(StrEnum):
    """
    Types of URL endpoints.

    The DATA type can be further formatted into different servers.
    """

    SITE = "https://kemono.su"
    DATA = "https://c{i}.kemono.su"
    API = "https://kemono.su/api/v1"
