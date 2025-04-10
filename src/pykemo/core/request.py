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

MOST_COMMON_DATA_SV: int = 3
"The number of the default server to use for DATA URL type."


def _parse_api_ver(api_version: Optional[APIVersion], base_url: UrlType) -> UrlLike:
    """
    Converts the API version to an actual string to be inserted in requests' URLs.
    
    :param api_version: The API version to be analyzed.
    :param base_url: The base URL. If it is of the :attr:`.UrlType.API` variant, use as-is.
                     If not, it's always ``None``.
    
    :type api_version: Optional[:class:`.APIVersion`]
    :type data_sv: :class:`int`, optional
    :type base_url: :class:`.UrlType`
    
    :return: The URL-like string ready to be used in URLs.
    :rtype: :type:`.UrlLike`
    """

    if not base_url.is_api():
        return ""

    return ("" if api_version is None else api_version.value)


async def request(method: "MethodLike",
                  endpoint: UrlLike,
                  *,
                  base_url: UrlType=UrlType.API,
                  api_version: Optional[APIVersion]=APIVersion.V1,
                  data_sv: int=MOST_COMMON_DATA_SV,
                  session: ClientSession,
                  **kwargs) -> "ClientResponse":
    """
    A customized wrap for `aiohttp.ClientSession.request() <https://docs.aiohttp.org/en/v3.11.13/client_reference.html#aiohttp.ClientSession.request>`_.

    :param method: The HTTP method to use.
    :param endpoint: The endpoint to map to.
    :param base_url: The root URL to use.
    :param api_version: The internal version of the API to use for the endpoints, defaults to :attr:`APIVersion.V1`
    :param data_sv: The server number to format the base URL with, in case it is of type :attr:`.UrlType.DATA`
    :param session: The session to use. This one is assumed to still be open and must be closed some
                    time afterwards.

    :type method: :type:`.MethodLike`
    :type endpoint: :type:`.UrlLike`
    :type base_url: Optional[:class:`.UrlType`]
    :type api_version: Optional[:class:`.APIVersion`]
    :type data_sv: :class:`int`, optional
    :type session: `ClientSession <https://docs.aiohttp.org/en/v3.11.13/client_reference.html#aiohttp.ClientSession>`_

    :return: The HTTP response.
    :rtype: `ClientResponse <https://docs.aiohttp.org/en/v3.11.13/client_reference.html#aiohttp.ClientResponse>`_
    """

    parsed_base_url = base_url.format_data(data_sv)

    return await session.request(
        method=method,
        url=f"{parsed_base_url}{_parse_api_ver(api_version, base_url)}{endpoint}",
        **kwargs
    )


async def get(endpoint: UrlLike,
              *,
              params=None,
              base_url: UrlType=UrlType.API,
              api_version: Optional[APIVersion]=APIVersion.V1,
              data_sv: int=MOST_COMMON_DATA_SV,
              session: ClientSession,
              **kwargs) -> "ClientResponse":
    """
    A wrap for `aiohttp.ClientSession.get() <https://docs.aiohttp.org/en/v3.11.13/client_reference.html#aiohttp.ClientSession.get>`_.

    :param endpoint: The endpoint to map to.
    :param params: A ``dict`` with the parameters of the request. Usually of type ``dict[str, int | str | None]``
    :param base_url: The root URL to use.
    :param api_version: The internal version of the API to use for the endpoints, defaults to :attr:`APIVersion.V1`
    :param data_sv: The server number to format the base URL with, in case it is of type :attr:`.UrlType.DATA`
    :param session: The session to use.

    :type endpoint: :type:`.UrlLike`
    :type params: Optional[:class:`dict`]
    :type base_url: Optional[:class:`.UrlType`]
    :type api_version: Optional[:class:`.APIVersion`]
    :type data_sv: :class:`int`, optional
    :type session: `ClientSession <https://docs.aiohttp.org/en/v3.11.13/client_reference.html#aiohttp.ClientSession>`_

    :return: The HTTP response.
    :rtype: `ClientResponse <https://docs.aiohttp.org/en/v3.11.13/client_reference.html#aiohttp.ClientResponse>`_
    """

    parsed_base_url = base_url.format_data(data_sv)

    return await session.get(
        url=f"{parsed_base_url}{_parse_api_ver(api_version, base_url)}{endpoint}",
        params=params,
        **kwargs
    )


async def options(endpoint: UrlLike,
                  *,
                  base_url: UrlType=UrlType.API,
                  api_version: Optional[APIVersion]=APIVersion.V1,
                  data_sv: int=MOST_COMMON_DATA_SV,
                  session: ClientSession,
                  **kwargs) -> "ClientResponse":
    """
    A wrap for `aiohttp.ClientSession.options() <https://docs.aiohttp.org/en/v3.11.13/client_reference.html#aiohttp.ClientSession.options>`_.
    
    :param endpoint: The endpoint to map to.
    :param base_url: The root URL to use.
    :param api_version: The internal version of the API to use for the endpoints, defaults to :attr:`APIVersion.V1`
    :param data_sv: The server number to format the base URL with, in case it is of type :attr:`.UrlType.DATA`
    :param session: The session to use.

    :type endpoint: :type:`.UrlLike`
    :type base_url: Optional[:class:`.UrlType`]
    :type api_version: Optional[:class:`.APIVersion`]
    :type data_sv: :class:`int`, optional
    :type session: `ClientSession <https://docs.aiohttp.org/en/v3.11.13/client_reference.html#aiohttp.ClientSession>`_

    :return: The HTTP response.
    :rtype: `ClientResponse <https://docs.aiohttp.org/en/v3.11.13/client_reference.html#aiohttp.ClientResponse>`_
    """

    parsed_base_url = base_url.format_data(data_sv)

    return await session.options(
        url=f"{parsed_base_url}{_parse_api_ver(api_version, base_url)}{endpoint}",
        **kwargs
    )


async def head(endpoint: UrlLike,
               *,
               base_url: UrlType=UrlType.API,
               api_version: Optional[APIVersion]=APIVersion.V1,
               data_sv: int=MOST_COMMON_DATA_SV,
               session: ClientSession,
               **kwargs) -> "ClientResponse":
    """
    A wrap for `aiohttp.ClientSession.head() <https://docs.aiohttp.org/en/v3.11.13/client_reference.html#aiohttp.ClientSession.head>`_.
    
    :param endpoint: The endpoint to map to.
    :param base_url: The root URL to use.
    :param api_version: The internal version of the API to use for the endpoints, defaults to :attr:`APIVersion.V1`
    :param data_sv: The server number to format the base URL with, in case it is of type :attr:`.UrlType.DATA`
    :param session: The session to use.

    :type endpoint: :type:`.UrlLike`
    :type base_url: Optional[:class:`.UrlType`]
    :type api_version: Optional[:class:`.APIVersion`]
    :type data_sv: :class:`int`, optional
    :type session: `ClientSession <https://docs.aiohttp.org/en/v3.11.13/client_reference.html#aiohttp.ClientSession>`_

    :return: The HTTP response.
    :rtype: `ClientResponse <https://docs.aiohttp.org/en/v3.11.13/client_reference.html#aiohttp.ClientResponse>`_
    """

    parsed_base_url = base_url.format_data(data_sv)

    return await session.head(
        url=f"{parsed_base_url}{_parse_api_ver(api_version, base_url)}{endpoint}",
        **kwargs
    )


async def post(endpoint: UrlLike,
               *,
               data=None,
               json=None,
               base_url: UrlType=UrlType.API,
               api_version: Optional[APIVersion]=APIVersion.V1,
               data_sv: int=MOST_COMMON_DATA_SV,
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
    :param data_sv: The server number to format the base URL with, in case it is of type :attr:`.UrlType.DATA`
    :param session: The session to use.

    :type endpoint: :type:`.UrlLike`
    :type data: Optional[:class:`Any`]
    :type json: Optional[:class:`dict`]
    :type base_url: Optional[:class:`.UrlType`]
    :type api_version: Optional[:class:`.APIVersion`]
    :type data_sv: :class:`int`, optional
    :type session: `ClientSession <https://docs.aiohttp.org/en/v3.11.13/client_reference.html#aiohttp.ClientSession>`_

    :return: The HTTP response.
    :rtype: `ClientResponse <https://docs.aiohttp.org/en/v3.11.13/client_reference.html#aiohttp.ClientResponse>`_
    """

    parsed_base_url = base_url.format_data(data_sv)

    return await session.post(
        url=f"{parsed_base_url}{_parse_api_ver(api_version, base_url)}{endpoint}",
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
              data_sv: int=MOST_COMMON_DATA_SV,
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
    :param data_sv: The server number to format the base URL with, in case it is of type :attr:`.UrlType.DATA`
    :param session: The session to use.

    :type endpoint: :type:`.UrlLike`
    :type data: Optional[:class:`Any`]
    :type json: Optional[:class:`dict`]
    :type base_url: Optional[:class:`.UrlType`]
    :type api_version: Optional[:class:`.APIVersion`]
    :type data_sv: :class:`int`, optional
    :type session: `ClientSession <https://docs.aiohttp.org/en/v3.11.13/client_reference.html#aiohttp.ClientSession>`_

    :return: The HTTP response.
    :rtype: `ClientResponse <https://docs.aiohttp.org/en/v3.11.13/client_reference.html#aiohttp.ClientResponse>`_
    """

    parsed_base_url = base_url.format_data(data_sv)

    return await session.put(
        url=f"{parsed_base_url}{_parse_api_ver(api_version, base_url)}{endpoint}",
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
                data_sv: int=MOST_COMMON_DATA_SV,
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
    :param data_sv: The server number to format the base URL with, in case it is of type :attr:`.UrlType.DATA`
    :param session: The session to use.

    :type endpoint: :type:`.UrlLike`
    :type data: Optional[:class:`Any`]
    :type json: Optional[:class:`dict`]
    :type base_url: Optional[:class:`.UrlType`]
    :type api_version: Optional[:class:`.APIVersion`]
    :type data_sv: :class:`int`, optional
    :type session: `ClientSession <https://docs.aiohttp.org/en/v3.11.13/client_reference.html#aiohttp.ClientSession>`_

    :return: The HTTP response.
    :rtype: `ClientResponse <https://docs.aiohttp.org/en/v3.11.13/client_reference.html#aiohttp.ClientResponse>`_
    """

    parsed_base_url = base_url.format_data(data_sv)

    return await session.patch(
        url=f"{parsed_base_url}{_parse_api_ver(api_version, base_url)}{endpoint}",
        data=data,
        json=json
        **kwargs
    )


async def delete(endpoint: UrlLike,
                 *,
                 base_url: UrlType=UrlType.API,
                 api_version: Optional[APIVersion]=APIVersion.V1,
                 data_sv: int=MOST_COMMON_DATA_SV,
                 session: ClientSession,
                 **kwargs) -> "ClientResponse":
    """
    A wrap for `aiohttp.ClientSession.delete() <https://docs.aiohttp.org/en/v3.11.13/client_reference.html#aiohttp.ClientSession.delete>`_.
    
    :param endpoint: The endpoint to map to.
    :param base_url: The root URL to use.
    :param api_version: The internal version of the API to use for the endpoints, defaults to :attr:`APIVersion.V1`
    :param data_sv: The server number to format the base URL with, in case it is of type :attr:`.UrlType.DATA`
    :param session: The session to use.

    :type endpoint: :type:`.UrlLike`
    :type base_url: Optional[:class:`.UrlType`]
    :type api_version: Optional[:class:`.APIVersion`]
    :type data_sv: :class:`int`, optional
    :type session: `ClientSession <https://docs.aiohttp.org/en/v3.11.13/client_reference.html#aiohttp.ClientSession>`_

    :return: The HTTP response.
    :rtype: `ClientResponse <https://docs.aiohttp.org/en/v3.11.13/client_reference.html#aiohttp.ClientResponse>`_
    """

    parsed_base_url = base_url.format_data(data_sv)

    return await session.delete(
        url=f"{parsed_base_url}{_parse_api_ver(api_version, base_url)}{endpoint}",
        **kwargs
    )
