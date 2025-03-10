"""
HTTP requests types.
"""

from enum import StrEnum
from typing import TypeAlias, Literal

MethodLiteral: TypeAlias = Literal["get", "options", "head", "post", "put", "patch", "delete"]


class HTTPRequestMethod(StrEnum):
    "HTTP Request Type."

    GET = "get"
    OPTIONS = "options"
    HEAD = "head"
    POST = "post"
    PUT = "put"
    PATCH = "patch"
    DELETE = "delete"

