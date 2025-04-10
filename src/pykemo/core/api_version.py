"""
API version enum module.
"""

from enum import StrEnum


class APIVersion(StrEnum):
    """
    Different versions of the API endpoint.

    Some endpoints might need a specific version to be prepended in the URL.
    """

    V1 = "v1"
    """
    The first and most common option for the endpoints.
    """

    V2 = "v2"
    """
    Used for some new, niche endpoints.
    """