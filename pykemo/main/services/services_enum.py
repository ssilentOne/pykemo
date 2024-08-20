"""
Enumeration of services that provide the users.
"""

from enum import StrEnum
from typing import Literal, TypeAlias, Union

_ServiceLiteral: TypeAlias = Literal["patreon", "fanbox", "gumroad", "subscribestar",
                                     "fantia", "boosty", "afdian", "discord", "dlsite"]
ServiceLike: TypeAlias = Union[_ServiceLiteral, "ServiceType"]


class ServiceType(StrEnum):
    "Service enum."

    PATREON = "patreon"
    FANBOX = "fanbox"
    GUMROAD = "gumroad"
    SUSCRIBE_STAR = "subscribestar"
    FANTIA = "fantia"
    BOOSTY = "boosty"
    AFDIAN = "afdian"
    DISCORD = "discord"
    DLSITE = "dlsite"
