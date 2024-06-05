"""
Custom Requests module.
"""

from enum import StrEnum
from typing import TYPE_CHECKING, TypeAlias

from requests import request as req

from ._request_types import HTTPRequestType

if TYPE_CHECKING:
    from os import PathLike

    from requests import Response

UrlLike: TypeAlias = "PathLike"
"""
A 'URL-like' is a string of the style `/a/b/c/d`.
"""

class UrlType(StrEnum):
    "Types of URL endpoints."

    SITE = "https://kemono.su"
    DATA = "https://c3.kemono.su"
    API = "https://kemono.su/api/v1"


def request(method: str, endpoint: UrlLike, url_type: UrlType=UrlType.API, **kwargs) -> "Response":
    """
    A customized mimic for `requests.request()`, with static url.
    """

    return req(method=method, url=f"{url_type}{endpoint}", **kwargs)


def get(endpoint: UrlLike, params=None, url_type: UrlType=UrlType.API, **kwargs) -> "Response":
    """
    A mimic for https://requests.readthedocs.io/projects/requests-html/en/latest/index.html#requests_html.HTMLSession.get.
    """

    return request(HTTPRequestType.GET, endpoint, params=params, url_type=url_type, **kwargs)


def options(endpoint: UrlLike, url_type: UrlType=UrlType.API, **kwargs) -> "Response":
    """
    A mimic for https://requests.readthedocs.io/projects/requests-html/en/latest/index.html#requests_html.HTMLSession.options.
    """

    return request(HTTPRequestType.OPTIONS, endpoint, url_type=url_type, **kwargs)


def head(endpoint: UrlLike, url_type: UrlType=UrlType.API, **kwargs) -> "Response":
    """
    A mimic for https://requests.readthedocs.io/projects/requests-html/en/latest/index.html#requests_html.HTMLSession.head.
    """

    return request(HTTPRequestType.HEAD, endpoint, url_type=url_type, **kwargs)


def post(endpoint: UrlLike, data=None, json=None, url_type: UrlType=UrlType.API, **kwargs) -> "Response":
    """
    A mimic for https://requests.readthedocs.io/projects/requests-html/en/latest/index.html#requests_html.HTMLSession.post.
    """

    return request(HTTPRequestType.POST, endpoint, data=data, json=json, url_type=url_type, **kwargs)


def put(endpoint: UrlLike, data=None, url_type: UrlType=UrlType.API, **kwargs) -> "Response":
    """
    A mimic for https://requests.readthedocs.io/projects/requests-html/en/latest/index.html#requests_html.HTMLSession.put.
    """

    return request(HTTPRequestType.PUT, endpoint, data=data, url_type=url_type, **kwargs)


def patch(endpoint: UrlLike, data=None, url_type: UrlType=UrlType.API, **kwargs) -> "Response":
    """
    A mimic for https://requests.readthedocs.io/projects/requests-html/en/latest/index.html#requests_html.HTMLSession.patch.
    """

    return request(HTTPRequestType.PATCH, endpoint, data=data, url_type=url_type, **kwargs)


def delete(endpoint: UrlLike, url_type: UrlType=UrlType.API, **kwargs) -> "Response":
    """
    A mimic for https://requests.readthedocs.io/projects/requests-html/en/latest/index.html#requests_html.HTMLSession.delete.
    """

    return request(HTTPRequestType.DELETE, endpoint, url_type=url_type, **kwargs)
