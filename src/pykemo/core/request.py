"""
Custom Requests module.
"""
from typing import TYPE_CHECKING, Optional, TypeAlias

from aiohttp import ClientSession
from aiohttp.typedefs import StrOrURL

from .api_versions import APIVersion
from .urltypes import UrlType

if TYPE_CHECKING:
    from aiohttp import ClientResponse

    from ._request_types import MethodLike

UrlLike: TypeAlias = StrOrURL
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


async def request(method: "MethodLike",
                  endpoint: UrlLike,
                  *,
                  base_url: UrlType=UrlType.API,
                  api_version: Optional[APIVersion]=APIVersion.V1,
                  session: ClientSession,
                  **kwargs) -> "ClientResponse":
    """
    A customized wrap for `aiohttp.ClientSession.request() <https://docs.aiohttp.org/en/v3.11.13/client_reference.html#aiohttp.ClientSession.request>`_.

    :param method: The HTTP method to use.
    :param endpoint: The endpoint to map to.
    :param base_url: The root URL to use.
    :param api_version: The internal version of the API to use for the endpoints, defaults to :attr:`APIVersion.V1`
    :param session: The session to use. This one is assumed to still be open and must be closed some
                    time afterwards.

    :type method: :type:`.MethodLike`
    :type endpoint: :type:`.UrlLike`
    :type base_url: Optional[:class:`.UrlType`]
    :type api_version: Optional[:class:`.APIVersion`]
    :type session: `ClientSession <https://docs.aiohttp.org/en/v3.11.13/client_reference.html#aiohttp.ClientSession>`_

    :return: The HTTP response.
    :rtype: `ClientResponse <https://docs.aiohttp.org/en/v3.11.13/client_reference.html#aiohttp.ClientResponse>`_
    """

    return await session.request(
        method=method,
        url=f"{base_url}{'' if api_version is None else api_version}{endpoint}",
        **kwargs
    )


async def get(endpoint: UrlLike,
              *,
              params=None,
              base_url: UrlType=UrlType.API,
              api_version: Optional[APIVersion]=APIVersion.V1,
              session: ClientSession,
              **kwargs) -> "ClientResponse":
    """
    A wrap for `aiohttp.ClientSession.get() <https://docs.aiohttp.org/en/v3.11.13/client_reference.html#aiohttp.ClientSession.get>`_.

    :param endpoint: The endpoint to map to.
    :param params: A ``dict`` with the parameters of the request. Usually of type ``dict[str, int | str | None]``
    :param base_url: The root URL to use.
    :param api_version: The internal version of the API to use for the endpoints, defaults to :attr:`APIVersion.V1`
    :param session: The session to use.

    :type endpoint: :type:`.UrlLike`
    :type params: Optional[:class:`dict`]
    :type base_url: Optional[:class:`.UrlType`]
    :type api_version: Optional[:class:`.APIVersion`]
    :type session: `ClientSession <https://docs.aiohttp.org/en/v3.11.13/client_reference.html#aiohttp.ClientSession>`_

    :return: The HTTP response.
    :rtype: `ClientResponse <https://docs.aiohttp.org/en/v3.11.13/client_reference.html#aiohttp.ClientResponse>`_
    """

    return await session.get(
        url=f"{base_url}{'' if api_version is None else api_version}{endpoint}",
        params=params,
        **kwargs
    )


async def options(endpoint: UrlLike,
                  *,
                  base_url: UrlType=UrlType.API,
                  api_version: Optional[APIVersion]=APIVersion.V1,
                  session: ClientSession,
                  **kwargs) -> "ClientResponse":
    """
    A wrap for `aiohttp.ClientSession.options() <https://docs.aiohttp.org/en/v3.11.13/client_reference.html#aiohttp.ClientSession.options>`_.
    
    :param endpoint: The endpoint to map to.
    :param base_url: The root URL to use.
    :param api_version: The internal version of the API to use for the endpoints, defaults to :attr:`APIVersion.V1`
    :param session: The session to use.

    :type endpoint: :type:`.UrlLike`
    :type base_url: Optional[:class:`.UrlType`]
    :type api_version: Optional[:class:`.APIVersion`]
    :type session: `ClientSession <https://docs.aiohttp.org/en/v3.11.13/client_reference.html#aiohttp.ClientSession>`_

    :return: The HTTP response.
    :rtype: `ClientResponse <https://docs.aiohttp.org/en/v3.11.13/client_reference.html#aiohttp.ClientResponse>`_
    """

    return await session.options(
        url=f"{base_url}{'' if api_version is None else api_version}{endpoint}",
        **kwargs
    )


async def head(endpoint: UrlLike,
               *,
               base_url: UrlType=UrlType.API,
               api_version: Optional[APIVersion]=APIVersion.V1,
               session: ClientSession,
               **kwargs) -> "ClientResponse":
    """
    A wrap for `aiohttp.ClientSession.head() <https://docs.aiohttp.org/en/v3.11.13/client_reference.html#aiohttp.ClientSession.head>`_.
    
    :param endpoint: The endpoint to map to.
    :param base_url: The root URL to use.
    :param api_version: The internal version of the API to use for the endpoints, defaults to :attr:`APIVersion.V1`
    :param session: The session to use.

    :type endpoint: :type:`.UrlLike`
    :type base_url: Optional[:class:`.UrlType`]
    :type api_version: Optional[:class:`.APIVersion`]
    :type session: `ClientSession <https://docs.aiohttp.org/en/v3.11.13/client_reference.html#aiohttp.ClientSession>`_

    :return: The HTTP response.
    :rtype: `ClientResponse <https://docs.aiohttp.org/en/v3.11.13/client_reference.html#aiohttp.ClientResponse>`_
    """

    return await session.head(
        url=f"{base_url}{'' if api_version is None else api_version}{endpoint}",
        **kwargs
    )


async def post(endpoint: UrlLike,
               *,
               data=None,
               json=None,
               base_url: UrlType=UrlType.API,
               api_version: Optional[APIVersion]=APIVersion.V1,
               session: ClientSession,
               **kwargs) -> "ClientResponse":
    """
    A wrap for `aiohttp.ClientSession.post() <https://docs.aiohttp.org/en/v3.11.13/client_reference.html#aiohttp.ClientSession.post>`_.

    .. warning:: ``data`` and ``json`` cannot be used both at once.

    :param endpoint: The endpoint to map to.
    :param data: Dictionary, list of file-like object to send in the body of the request, defaults to ``None``
    :param json: JSON-like to send in the body of the request, defaults to ``None``
    :param base_url: The root URL to use.
    :param api_version: The internal version of the API to use for the endpoints, defaults to :attr:`APIVersion.V1`
    :param session: The session to use.

    :type endpoint: :type:`.UrlLike`
    :type data: Optional[:class:`Any`]
    :type json: Optional[:class:`dict`]
    :type base_url: Optional[:class:`.UrlType`]
    :type api_version: Optional[:class:`.APIVersion`]
    :type session: `ClientSession <https://docs.aiohttp.org/en/v3.11.13/client_reference.html#aiohttp.ClientSession>`_

    :return: The HTTP response.
    :rtype: `ClientResponse <https://docs.aiohttp.org/en/v3.11.13/client_reference.html#aiohttp.ClientResponse>`_
    """

    return await session.post(
        url=f"{base_url}{'' if api_version is None else api_version}{endpoint}",
        data=data,
        json=json,
        **kwargs
    )


async def put(endpoint: UrlLike,
              *,
              data=None,
              json=None,
              base_url: UrlType=UrlType.API,
              api_version: Optional[APIVersion]=APIVersion.V1,
              session: ClientSession,
              **kwargs) -> "ClientResponse":
    """
    A wrap for `aiohttp.ClientSession.put() <https://docs.aiohttp.org/en/v3.11.13/client_reference.html#aiohttp.ClientSession.put>`_.

    .. warning:: ``data`` and ``json`` cannot be used both at once.

    :param endpoint: The endpoint to map to.
    :param data: Dictionary, list of file-like object to send in the body of the request, defaults to ``None``
    :param json: JSON-like to send in the body of the request, defaults to ``None``.
    :param base_url: The root URL to use.
    :param api_version: The internal version of the API to use for the endpoints, defaults to :attr:`APIVersion.V1`
    :param session: The session to use.

    :type endpoint: :type:`.UrlLike`
    :type data: Optional[:class:`Any`]
    :type json: Optional[:class:`dict`]
    :type base_url: Optional[:class:`.UrlType`]
    :type api_version: Optional[:class:`.APIVersion`]
    :type session: `ClientSession <https://docs.aiohttp.org/en/v3.11.13/client_reference.html#aiohttp.ClientSession>`_

    :return: The HTTP response.
    :rtype: `ClientResponse <https://docs.aiohttp.org/en/v3.11.13/client_reference.html#aiohttp.ClientResponse>`_
    """

    return await session.put(
        url=f"{base_url}{'' if api_version is None else api_version}{endpoint}",
        data=data,
        json=json
        **kwargs
    )


async def patch(endpoint: UrlLike,
                *,
                data=None,
                json=None,
                base_url: UrlType=UrlType.API,
                api_version: Optional[APIVersion]=APIVersion.V1,
                session: ClientSession,
                **kwargs) -> "ClientResponse":
    """
    A wrap for `aiohttp.ClientSession.patch() <https://docs.aiohttp.org/en/v3.11.13/client_reference.html#aiohttp.ClientSession.patch>`_.

    .. warning:: ``data`` and ``json`` cannot be used both at once.

    :param endpoint: The endpoint to map to.
    :param data: Dictionary, list of file-like object to send in the body of the request, defaults to ``None``
    :param json: JSON-like to send in the body of the request, defaults to ``None``.
    :param base_url: The root URL to use.
    :param api_version: The internal version of the API to use for the endpoints, defaults to :attr:`APIVersion.V1`
    :param session: The session to use.

    :type endpoint: :type:`.UrlLike`
    :type data: Optional[:class:`Any`]
    :type json: Optional[:class:`dict`]
    :type base_url: Optional[:class:`.UrlType`]
    :type api_version: Optional[:class:`.APIVersion`]
    :type session: `ClientSession <https://docs.aiohttp.org/en/v3.11.13/client_reference.html#aiohttp.ClientSession>`_

    :return: The HTTP response.
    :rtype: `ClientResponse <https://docs.aiohttp.org/en/v3.11.13/client_reference.html#aiohttp.ClientResponse>`_
    """

    return await session.patch(
        url=f"{base_url}{'' if api_version is None else api_version}{endpoint}",
        data=data,
        json=json
        **kwargs
    )


async def delete(endpoint: UrlLike,
                 *,
                 base_url: UrlType=UrlType.API,
                 api_version: Optional[APIVersion]=APIVersion.V1,
                 session: ClientSession,
                 **kwargs) -> "ClientResponse":
    """
    A wrap for `aiohttp.ClientSession.delete() <https://docs.aiohttp.org/en/v3.11.13/client_reference.html#aiohttp.ClientSession.delete>`_.
    
    :param endpoint: The endpoint to map to.
    :param base_url: The root URL to use.
    :param api_version: The internal version of the API to use for the endpoints, defaults to :attr:`APIVersion.V1`
    :param session: The session to use.

    :type endpoint: :type:`.UrlLike`
    :type base_url: Optional[:class:`.UrlType`]
    :type api_version: Optional[:class:`.APIVersion`]
    :type session: `ClientSession <https://docs.aiohttp.org/en/v3.11.13/client_reference.html#aiohttp.ClientSession>`_

    :return: The HTTP response.
    :rtype: `ClientResponse <https://docs.aiohttp.org/en/v3.11.13/client_reference.html#aiohttp.ClientResponse>`_
    """

    return await session.delete(
        url=f"{base_url}{'' if api_version is None else api_version}{endpoint}",
        **kwargs
    )
