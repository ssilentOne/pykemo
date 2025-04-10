"""
HTTP requests types.
"""

from enum import StrEnum
from typing import TypeAlias, Literal, Union

MethodLiteral: TypeAlias = Literal["get", "options", "head", "post", "put", "patch", "delete"]
MethodLike: TypeAlias = Union["HTTPRequestMethod", MethodLiteral]

class HTTPRequestMethod(StrEnum):
    "HTTP Request Type."

    GET = "get"
    "A HTTP 'GET' request type."

    OPTIONS = "options"
    "A HTTP 'OPTIONS' request type."

    HEAD = "head"
    "A HTTP 'HEAD' request type."

    POST = "post"
    "A HTTP 'POST' request type."

    PUT = "put"
    "A HTTP 'PUT' request type."

    PATCH = "patch"
    "A HTTP 'PATCH' request type."

    DELETE = "delete"
    "A HTTP 'DELETE' request type."
