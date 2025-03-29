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
    "A [Patreon](https://www.patreon.com/) service type."

    FANBOX = "fanbox"
    "A [Fanbox](https://www.fanbox.cc/) service type."

    GUMROAD = "gumroad"
    "A [Gumroad](https://gumroad.com/) service type."

    SUSCRIBE_STAR = "subscribestar"
    "A [SubscribeStar](https://www.subscribestar.com/) service type."

    FANTIA = "fantia"
    "A [Fantia](https://fantia.jp/) service type."

    BOOSTY = "boosty"
    "A [Boosty](https://boosty.to) service type."

    AFDIAN = "afdian"
    "A [Afdian](https://afdian.com/) service type."

    DISCORD = "discord"
    "A [Discord](https://discord.com/) service type."

    DLSITE = "dlsite"
    "A [DLSite](https://www.dlsite.com/) service type."
