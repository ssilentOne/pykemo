"""
Services checks module.
"""

from typing import TYPE_CHECKING

from ..exceptions import (
    IncorrectServiceError,
    NotDiscordError,
    NotFanboxError,
    PyKemoException,
)
from ..services import ServiceType

if TYPE_CHECKING:
    from ..creators import Creator


def exc_check(condition: bool, exception: PyKemoException) -> None:
    """
    If the condition is True, raises the exception given.
    """

    if condition:
        raise exception


def correct_service_check(creator: "Creator", service: ServiceType) -> None:
    """
    Checks for a correct service.
    """

    exc_check(creator.service != service, IncorrectServiceError(creator.service))


def incorrect_service_check(creator: "Creator", service: ServiceType) -> None:
    """
    Checks for an incorrect service.
    """

    exc_check(creator.service == service, IncorrectServiceError(service))


def check_if_fanbox(creator: "Creator") -> None:
    """
    Checks if a creator's service is Fanbox. Otherwise, throws an exception.
    """

    exc_check(creator.service != ServiceType.FANBOX, NotFanboxError(creator.service))


def check_if_discord(creator: "Creator") -> None:
    """
    Checks if a creator's service is Discord. Otherwise, throws an exception.
    """

    exc_check(creator.service != ServiceType.DISCORD, NotDiscordError(creator.service))