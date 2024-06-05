"""
Enumeration of services that provide the users.
"""

from enum import StrEnum
from typing import TypeAlias, Union

ServiceLike: TypeAlias = Union[str, "ServiceType"]


class ServiceType(StrEnum):
    "Service enum."

    PATREON = "patreon"
    FANBOX = "fanbox"
    GUMROAD = "gumroad"
    SUSCRIBE_STAR = "suscribe_star"
    FANTIA = "fantia"
    BOOSTY = "boosty"
    AFDIAN = "afdian"
    DISCORD = "discord"
