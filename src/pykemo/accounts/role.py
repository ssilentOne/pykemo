"""
Account role module.
"""

from enum import StrEnum

class AccountRole(StrEnum):
    "Different roles of a Kemono account."

    CONSUMER = "consumer"
    MODERATOR = "moderator"
    ADMINISTRATOR = "administrator"