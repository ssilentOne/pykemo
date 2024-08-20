"""
Enumeration of services that provide the users.
"""

from enum import StrEnum
from typing import Literal, TypeAlias, Union

_ServiceLiteral: TypeAlias = Literal["patreon", "fanbox", "gumroad", "suscribe_star",
                                     "fantia", "boosty", "afdian", "discord"]
ServiceLike: TypeAlias = Union[_ServiceLiteral, "ServiceType"]


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
