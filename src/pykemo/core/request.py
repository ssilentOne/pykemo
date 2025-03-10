"""
Custom Requests module.
"""
from typing import TYPE_CHECKING, TypeAlias, Union

from aiohttp import ClientSession

from ._request_types import HTTPRequestMethod, MethodLiteral
from .urltypes import UrlType

if TYPE_CHECKING:
    from os import PathLike

    from aiohttp import ClientResponse

UrlLike: TypeAlias = "PathLike"
"""
A 'URL-like' is a string of the style `/a/b/c/d`.
"""

MethodLike: TypeAlias = Union[HTTPRequestMethod, MethodLiteral]

MAX_RETRIES: int = 10
"Max retries for a request."

BACKOFF_FACTOR: float = 0.1
"The backoff factor for calculating delays."

FORCELIST: list[int] = [429]
"A list of statues codes to be wary of. These will trigger a retry."

ADAPTER_PREFIX: UrlLike = "https://"
"A prefix for URLs that trigger the custom HTTP adapter."


async def request(method: MethodLike,
                  endpoint: UrlLike,
                  *,
                  base_url: UrlType=UrlType.API,
                  session: ClientSession,
                  **kwargs) -> "ClientResponse":
    """
    A customized wrap for `aiohttp.ClientSession.request() <https://docs.aiohttp.org/en/v3.11.13/client_reference.html#aiohttp.ClientSession.request>`_.

    :param method: The HTTP method to use.
    :param endpoint: The endpoint to map to.
    :param base_url: The root URL to use.
    :param session: The session to use. This one is assumed to still be open and must be closed some
                    time afterwards.

    :type method: :type:`.MethodLike`
    :type endpoint: :type:`.UrlLike`
    :type base_url: Optional[:class:`.UrlType`]
    :type session: `ClientSession <https://docs.aiohttp.org/en/v3.11.13/client_reference.html#aiohttp.ClientSession>`_

    :return: The HTTP response.
    :rtype: `ClientResponse <https://docs.aiohttp.org/en/v3.11.13/client_reference.html#aiohttp.ClientResponse>`_
    """

    return await session.request(method=method, url=f"{base_url}{endpoint}", **kwargs)


async def get(endpoint: UrlLike,
              *,
              params=None,
              base_url: UrlType=UrlType.API,
              session: ClientSession,
              **kwargs) -> "ClientResponse":
    """
    A wrap for `aiohttp.ClientSession.get() <https://docs.aiohttp.org/en/v3.11.13/client_reference.html#aiohttp.ClientSession.get>`_.

    :param endpoint: The endpoint to map to.
    :param params: A ``dict`` with the parameters of the request. Usually of type ``dict[str, int | str | None]``
    :param base_url: The root URL to use.
    :param session: The session to use.

    :type endpoint: :type:`.UrlLike`
    :type params: Optional[:class:`dict`]
    :type base_url: Optional[:class:`.UrlType`]
    :type session: `ClientSession <https://docs.aiohttp.org/en/v3.11.13/client_reference.html#aiohttp.ClientSession>`_

    :return: The HTTP response.
    :rtype: `ClientResponse <https://docs.aiohttp.org/en/v3.11.13/client_reference.html#aiohttp.ClientResponse>`_
    """

    return await request(HTTPRequestMethod.GET,
                         endpoint,
                         params=params,
                         base_url=base_url,
                         session=session,
                         **kwargs)


async def options(endpoint: UrlLike,
                  *,
                  base_url: UrlType=UrlType.API,
                  session: ClientSession,
                  **kwargs) -> "ClientResponse":
    """
    A wrap for `aiohttp.ClientSession.options() <https://docs.aiohttp.org/en/v3.11.13/client_reference.html#aiohttp.ClientSession.options>`_.
    
    :param endpoint: The endpoint to map to.
    :param base_url: The root URL to use.
    :param session: The session to use.

    :type endpoint: :type:`.UrlLike`
    :type base_url: Optional[:class:`.UrlType`]
    :type session: `ClientSession <https://docs.aiohttp.org/en/v3.11.13/client_reference.html#aiohttp.ClientSession>`_

    :return: The HTTP response.
    :rtype: `ClientResponse <https://docs.aiohttp.org/en/v3.11.13/client_reference.html#aiohttp.ClientResponse>`_
    """

    return await request(HTTPRequestMethod.OPTIONS, endpoint, base_url=base_url, session=session, **kwargs)


async def head(endpoint: UrlLike,
               *,
               base_url: UrlType=UrlType.API,
               session: ClientSession,
               **kwargs) -> "ClientResponse":
    """
    A wrap for `aiohttp.ClientSession.head() <https://docs.aiohttp.org/en/v3.11.13/client_reference.html#aiohttp.ClientSession.head>`_.
    
    :param endpoint: The endpoint to map to.
    :param base_url: The root URL to use.
    :param session: The session to use.

    :type endpoint: :type:`.UrlLike`
    :type base_url: Optional[:class:`.UrlType`]
    :type session: `ClientSession <https://docs.aiohttp.org/en/v3.11.13/client_reference.html#aiohttp.ClientSession>`_

    :return: The HTTP response.
    :rtype: `ClientResponse <https://docs.aiohttp.org/en/v3.11.13/client_reference.html#aiohttp.ClientResponse>`_
    """

    return await request(HTTPRequestMethod.HEAD, endpoint, base_url=base_url, session=session, **kwargs)


async def post(endpoint: UrlLike,
               *,
               data=None,
               json=None,
               base_url: UrlType=UrlType.API,
               session: ClientSession,
               **kwargs) -> "ClientResponse":
    """
    A wrap for `aiohttp.ClientSession.post() <https://docs.aiohttp.org/en/v3.11.13/client_reference.html#aiohttp.ClientSession.post>`_.
    
    :param endpoint: The endpoint to map to.
    :param data: Dictionary, list of file-like object to send in the body of the request.
    :param json: JSON-like to send in the body of the request.
    :param base_url: The root URL to use.
    :param session: The session to use.

    :type endpoint: :type:`.UrlLike`
    :type data: Optional[:class:`Any`]
    :type json: Optional[:class:`dict`]
    :type base_url: Optional[:class:`.UrlType`]
    :type session: `ClientSession <https://docs.aiohttp.org/en/v3.11.13/client_reference.html#aiohttp.ClientSession>`_

    :return: The HTTP response.
    :rtype: `ClientResponse <https://docs.aiohttp.org/en/v3.11.13/client_reference.html#aiohttp.ClientResponse>`_
    """

    return await request(HTTPRequestMethod.POST,
                         endpoint,
                         data=data,
                         json=json,
                         base_url=base_url,
                         session=session,
                         **kwargs)


async def put(endpoint: UrlLike,
              *,
              data=None,
              base_url: UrlType=UrlType.API,
              session: ClientSession,
              **kwargs) -> "ClientResponse":
    """
    A wrap for `aiohttp.ClientSession.put() <https://docs.aiohttp.org/en/v3.11.13/client_reference.html#aiohttp.ClientSession.put>`_.
    
    :param endpoint: The endpoint to map to.
    :param data: Dictionary, list of file-like object to send in the body of the request.
    :param base_url: The root URL to use.
    :param session: The session to use.

    :type endpoint: :type:`.UrlLike`
    :type data: Optional[:class:`Any`]
    :type base_url: Optional[:class:`.UrlType`]
    :type session: `ClientSession <https://docs.aiohttp.org/en/v3.11.13/client_reference.html#aiohttp.ClientSession>`_

    :return: The HTTP response.
    :rtype: `ClientResponse <https://docs.aiohttp.org/en/v3.11.13/client_reference.html#aiohttp.ClientResponse>`_
    """

    return await request(HTTPRequestMethod.PUT,
                         endpoint,
                         data=data,
                         base_url=base_url,
                         session=session,
                         **kwargs)


async def patch(endpoint: UrlLike,
                *,
                data=None,
                base_url: UrlType=UrlType.API,
                session: ClientSession,
                **kwargs) -> "ClientResponse":
    """
    A wrap for `aiohttp.ClientSession.patch() <https://docs.aiohttp.org/en/v3.11.13/client_reference.html#aiohttp.ClientSession.patch>`_.
    
    :param endpoint: The endpoint to map to.
    :param data: Dictionary, list of file-like object to send in the body of the request.
    :param base_url: The root URL to use.
    :param session: The session to use.

    :type endpoint: :type:`.UrlLike`
    :type data: Optional[:class:`Any`]
    :type base_url: Optional[:class:`.UrlType`]
    :type session: `ClientSession <https://docs.aiohttp.org/en/v3.11.13/client_reference.html#aiohttp.ClientSession>`_

    :return: The HTTP response.
    :rtype: `ClientResponse <https://docs.aiohttp.org/en/v3.11.13/client_reference.html#aiohttp.ClientResponse>`_
    """

    return await request(HTTPRequestMethod.PATCH,
                         endpoint,
                         data=data,
                         base_url=base_url,
                         session=session,
                         **kwargs)


async def delete(endpoint: UrlLike,
                 *,
                 base_url: UrlType=UrlType.API,
                 session: ClientSession,
                 **kwargs) -> "ClientResponse":
    """
    A wrap for `aiohttp.ClientSession.delete() <https://docs.aiohttp.org/en/v3.11.13/client_reference.html#aiohttp.ClientSession.delete>`_.
    
    :param endpoint: The endpoint to map to.
    :param base_url: The root URL to use.
    :param session: The session to use.

    :type endpoint: :type:`.UrlLike`
    :type base_url: Optional[:class:`.UrlType`]
    :type session: `ClientSession <https://docs.aiohttp.org/en/v3.11.13/client_reference.html#aiohttp.ClientSession>`_

    :return: The HTTP response.
    :rtype: `ClientResponse <https://docs.aiohttp.org/en/v3.11.13/client_reference.html#aiohttp.ClientResponse>`_
    """

    return await request(HTTPRequestMethod.DELETE, endpoint, base_url=base_url, session=session, **kwargs)
