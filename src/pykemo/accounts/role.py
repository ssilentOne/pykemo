"""
Account role module.
"""

from enum import StrEnum

class AccountRole(StrEnum):
    "Different roles of a Kemono account."

    CONSUMER = "consumer"
    "A normal consumer account."

    MODERATOR = "moderator"
    "A moderator account that controls some structures."

    ADMINISTRATOR = "administrator"
    "An administrator account with full privileges."
