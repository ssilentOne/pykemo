"""
Creator link current status module.
"""

from enum import StrEnum


class CreatorLinkStatus(StrEnum):
    "The current status of a creator link request."

    PENDING = "pending"
    "A creator link pending of review."

    # It is implied that other types exist, but as of now, without an
    # actual moderator account to test with, there is no way to know for certain.
    # The API documentation only shows the 'pending' variant.
    OTHER = "other"
    "A creator link in an unknow situation."
