"""
Custom services exceptions module.
"""

from typing import TYPE_CHECKING

from .general import PyKemoException

if TYPE_CHECKING:
    from ..services import ServiceType


class IncorrectService(PyKemoException):
    "An incorrect service was selected for something."

    def __init__(self, service_type: "ServiceType") -> None:
        "Initializes the incorrect service error instance with custom fields."

        super().__init__(f"Service type '{service_type}' is invalid for this operation.")


class NotFanbox(PyKemoException):
    "The service used is not Fanbox."

    def __init__(self, service_type: "ServiceType") -> None:
        "Initializes the instance with custom fields."

        super().__init__(f"Only 'fanbox' is valid for this operation, not '{service_type}'.")


class NotDiscord(PyKemoException):
    "The service used is not Discord."

    def __init__(self, service_type: "ServiceType") -> None:
        "Initializes the instance with custom fields."

        super().__init__(f"Only 'discord' is valid for this operation, not '{service_type}'.")
