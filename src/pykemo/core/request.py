"""
Custom Requests module.
"""
from typing import TYPE_CHECKING, Optional, TypeAlias

from grequests import map as async_map
from grequests import request as async_req
from requests import Session
from requests.adapters import HTTPAdapter, Retry

from ._request_types import HTTPRequestType
from .urltypes import UrlType

if TYPE_CHECKING:
    from os import PathLike

    from grequests import AsyncRequest
    from requests import Response

UrlLike: TypeAlias = "PathLike"
"""
A 'URL-like' is a string of the style `/a/b/c/d`.
"""

MAX_RETRIES: int = 10
"Max retries for a request."

BACKOFF_FACTOR: float = 0.1
"The backoff factor for calculating delays."

FORCELIST: list[int] = [429]
"A list of statues codes to be wary of. These will trigger a retry."

ADAPTER_PREFIX: UrlLike = "https://"
"A prefix for URLs that trigger the custom HTTP adapter."


def request(method: str, endpoint: UrlLike, url_type: UrlType=UrlType.API, **kwargs) -> "Response":
    """
    A customized wrap for `requests.Session.request() <https://requests.readthedocs.io/en/latest/api/#requests.Session.request>_`, with static url and its own session.

    :param method: The HTTP method to use.
    :param endpoint: The endpoint to map to.
    :param url_type: The root URL to use.

    :type method: :class:`str`
    :type endpoint: :type:`.UrlLike`
    :type url_type: Optional[:class:`.UrlType`]

    :return: The HTTP response.
    :rtype: `Response <https://requests.readthedocs.io/en/latest/api/#requests.Response>`_
    """

    with Session() as session:
        session.mount(ADAPTER_PREFIX, HTTPAdapter(max_retries=Retry(total=MAX_RETRIES,
                                                                    backoff_factor=BACKOFF_FACTOR,
                                                                    status_forcelist=FORCELIST)))
        res = session.request(method=method, url=f"{url_type}{endpoint}", **kwargs)
    return res


def async_request(method: str, endpoint: UrlLike, url_type: UrlType=UrlType.API, **kwargs) -> "AsyncRequest":
    """
    A customized wrapper for grequests' :meth:`request()` with its own session. Note that this does not
    return a response, but rather an unsent asynchronous request.

    :param method: The HTTP method to use.
    :param endpoint: The endpoint to map to.
    :param url_type: The root URL to use.

    :type method: :class:`str`
    :type endpoint: :type:`.UrlLike`
    :type url_type: Optional[:class:`.UrlType`]

    :return: An unsent asynchronous request.
    :rtype: :class:`grequests.AsyncRequest`
    """

    retry_session = Session()
    retry_session.mount(ADAPTER_PREFIX, HTTPAdapter(max_retries=Retry(total=MAX_RETRIES,
                                                                      backoff_factor=BACKOFF_FACTOR,
                                                                      status_forcelist=FORCELIST)))
    return async_req(method=method, url=f"{url_type}{endpoint}", session=retry_session, **kwargs)


def get(endpoint: UrlLike, params=None, url_type: UrlType=UrlType.API, **kwargs) -> "Response":
    """
    A wrap for `requests.get() <https://requests.readthedocs.io/projects/requests-html/en/latest/index.html#requests_html.HTMLSession.get>`_.

    :param endpoint: The endpoint to map to.
    :param params: A ``dict`` with the parameters of the request. Usually of type ``dict[str, int | str | None]``
    :param url_type: The root URL to use.

    :type endpoint: :type:`.UrlLike`
    :type params: Optional[:class:`dict`]
    :type url_type: Optional[:class:`.UrlType`]

    :return: The HTTP response.
    :rtype: `Response <https://requests.readthedocs.io/en/latest/api/#requests.Response>`_
    """

    return request(HTTPRequestType.GET, endpoint, params=params, url_type=url_type, **kwargs)


def options(endpoint: UrlLike, url_type: UrlType=UrlType.API, **kwargs) -> "Response":
    """
    A wrap for `requests.options() <https://requests.readthedocs.io/projects/requests-html/en/latest/index.html#requests_html.HTMLSession.options>`_.
    
    :param endpoint: The endpoint to map to.
    :param url_type: The root URL to use.

    :type endpoint: :type:`.UrlLike`
    :type url_type: Optional[:class:`.UrlType`]

    :return: The HTTP response.
    :rtype: `Response <https://requests.readthedocs.io/en/latest/api/#requests.Response>`_
    """

    return request(HTTPRequestType.OPTIONS, endpoint, url_type=url_type, **kwargs)


def head(endpoint: UrlLike, url_type: UrlType=UrlType.API, **kwargs) -> "Response":
    """
    A wrap for `requests.head() <https://requests.readthedocs.io/projects/requests-html/en/latest/index.html#requests_html.HTMLSession.head>`_.
    
    :param endpoint: The endpoint to map to.
    :param url_type: The root URL to use.

    :type endpoint: :type:`.UrlLike`
    :type url_type: Optional[:class:`.UrlType`]

    :return: The HTTP response.
    :rtype: `Response <https://requests.readthedocs.io/en/latest/api/#requests.Response>`_
    """

    return request(HTTPRequestType.HEAD, endpoint, url_type=url_type, **kwargs)


def post(endpoint: UrlLike, data=None, json=None, url_type: UrlType=UrlType.API, **kwargs) -> "Response":
    """
    A wrap for `requests.post() <https://requests.readthedocs.io/projects/requests-html/en/latest/index.html#requests_html.HTMLSession.post>`_.
    
    :param endpoint: The endpoint to map to.
    :param data: Dictionary, list of file-like object to send in the body of the request.
    :param json: JSON-like to send in the body of the request.
    :param url_type: The root URL to use.

    :type endpoint: :type:`.UrlLike`
    :type data: Optional[:class:`Any`]
    :type json: Optional[:class:`dict`]
    :type url_type: Optional[:class:`.UrlType`]

    :return: The HTTP response.
    :rtype: `Response <https://requests.readthedocs.io/en/latest/api/#requests.Response>`_
    """

    return request(HTTPRequestType.POST, endpoint, data=data, json=json, url_type=url_type, **kwargs)


def put(endpoint: UrlLike, data=None, url_type: UrlType=UrlType.API, **kwargs) -> "Response":
    """
    A wrap for `requests.put() <https://requests.readthedocs.io/projects/requests-html/en/latest/index.html#requests_html.HTMLSession.put>`_.
    
    :param endpoint: The endpoint to map to.
    :param data: Dictionary, list of file-like object to send in the body of the request.
    :param url_type: The root URL to use.

    :type endpoint: :type:`.UrlLike`
    :type data: Optional[:class:`Any`]
    :type url_type: Optional[:class:`.UrlType`]

    :return: The HTTP response.
    :rtype: `Response <https://requests.readthedocs.io/en/latest/api/#requests.Response>`_
    """

    return request(HTTPRequestType.PUT, endpoint, data=data, url_type=url_type, **kwargs)


def patch(endpoint: UrlLike, data=None, url_type: UrlType=UrlType.API, **kwargs) -> "Response":
    """
    A wrap for `requests.patch() <https://requests.readthedocs.io/projects/requests-html/en/latest/index.html#requests_html.HTMLSession.patch>`_.
    
    :param endpoint: The endpoint to map to.
    :param data: Dictionary, list of file-like object to send in the body of the request.
    :param url_type: The root URL to use.

    :type endpoint: :type:`.UrlLike`
    :type data: Optional[:class:`Any`]
    :type url_type: Optional[:class:`.UrlType`]

    :return: The HTTP response.
    :rtype: `Response <https://requests.readthedocs.io/en/latest/api/#requests.Response>`_
    """

    return request(HTTPRequestType.PATCH, endpoint, data=data, url_type=url_type, **kwargs)


def delete(endpoint: UrlLike, url_type: UrlType=UrlType.API, **kwargs) -> "Response":
    """
    A wrap for `requests.delete() <https://requests.readthedocs.io/projects/requests-html/en/latest/index.html#requests_html.HTMLSession.delete>`_.
    
    :param endpoint: The endpoint to map to.
    :param url_type: The root URL to use.

    :type endpoint: :type:`.UrlLike`
    :type url_type: Optional[:class:`.UrlType`]

    :return: The HTTP response.
    :rtype: `Response <https://requests.readthedocs.io/en/latest/api/#requests.Response>`_
    """

    return request(HTTPRequestType.DELETE, endpoint, url_type=url_type, **kwargs)


def async_get(endpoint: UrlLike, params=None, url_type: UrlType=UrlType.API, **kwargs) -> "AsyncRequest":
    """
    A wrapper for grequests' :meth:`get()`.

    :param endpoint: The endpoint to map to.
    :param params: A ``dict`` with the parameters of the request. Usually of type ``dict[str, int | str | None]``
    :param url_type: The root URL to use.

    :type endpoint: :type:`.UrlLike`
    :type params: Optional[:class:`dict`]
    :type url_type: Optional[:class:`.UrlType`]

    :return: An unsent asynchronous request.
    :rtype: :class:`grequests.AsyncRequest`

    .. note:: Note that this does not return a response, but rather an unsent asynchronous request.
    """

    return async_request(HTTPRequestType.GET, endpoint, params=params, url_type=url_type, **kwargs)


def map(endpoints: list[UrlLike],
        url_type: UrlType=UrlType.API,
        size: Optional[int]=None,
        **kwargs) -> list["Response"]:
    """
    A wrapper for grequests' :meth:`map()`. 

    .. note:: This one accepts `endpoints as strings`, not already created unsent requests.

    :param endpoints: A list of all the endpoints to process.
    :param url_type: The root URL to use.
    :param size: How big is each batch of asynchronous requests.

    :type endpoints: list[:type:`.UrlLike`]
    :type url_type: Optional[:class:`.UrlType`]
    :type size: Optional[:class:`int`]

    :return: The list of completed responses.
    :rtype: list[`Response <https://requests.readthedocs.io/en/latest/api/#requests.Response>`_]
    """

    req_endpoints = (async_get(endpoint, url_type=url_type, **kwargs)
                     for endpoint in endpoints)
    
    return async_map(req_endpoints, size=size, **kwargs)
