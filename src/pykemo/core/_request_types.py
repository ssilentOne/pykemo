"""
HTTP requests types.
"""

from enum import StrEnum

class HTTPRequestType(StrEnum):
    "HTTP Request Type."

    GET = "get"
    OPTIONS = "options"
    HEAD = "head"
    POST = "post"
    PUT = "put"
    PATCH = "patch"
    DELETE = "delete"

