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
    "A `Patreon <https://www.patreon.com/>`_ service type."

    FANBOX = "fanbox"
    "A `Fanbox <https://www.fanbox.cc/>`_ service type."

    GUMROAD = "gumroad"
    "A `Gumroad <https://gumroad.com/>`_ service type."

    SUSCRIBE_STAR = "subscribestar"
    "A `SubscribeStar <https://www.subscribestar.com/>`_ service type."

    FANTIA = "fantia"
    "A `Fantia <https://fantia.jp/>`_ service type."

    BOOSTY = "boosty"
    "A `Boosty <https://boosty.to>`_ service type."

    AFDIAN = "afdian"
    "A `Afdian <https://afdian.com/>`_ service type."

    DISCORD = "discord"
    "A `Discord <https://discord.com/>`_ service type."

    DLSITE = "dlsite"
    "A `DLSite <https://www.dlsite.com/>`_ service type."
