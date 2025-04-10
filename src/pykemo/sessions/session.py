"""
Kemono session module.
"""

from types import TracebackType
from typing import TYPE_CHECKING, Optional, Self, TypeAlias

from aiohttp import ClientSession

from ..core import (
    APIVersion,
    UrlType,
    delete,
    get,
    head,
    options,
    patch,
    post,
    put,
    request,
)

if TYPE_CHECKING:
    from aiohttp import ClientResponse

    from ..core import UrlLike

TokenValue: TypeAlias = str

SITE_DOMAIN: "UrlLike" = "kemono.su"
"""
The site domain. Not necessarily the same as the one with the adapter.
"""


class KemoSession:
    """
    Kemono HTTP session.
    """

    def __init__(self) -> None:
        """
        Initializes the instance with custom adapters.
        """

        self.__aio_session: ClientSession = ClientSession()


    @classmethod
    def with_token(cls, cookie_auth: TokenValue) -> Self:
        """
        Creates a session instace, with the session cookie set.

        :param cookie_auth: The session cookie that can be found after a successful login.
                            Pykemo cannot find this on its own, the user must provide it.

        :type cookie_auth: :type:`.TokenValue`
        
        :return: An instance of the session.
        :rtype: :class:`.KemoSession`
        """

        obj = cls()
        obj.set_session_cookie(cookie_auth)

        return obj


    async def close(self) -> None:
        """
        A wrapper for closing the async session.
        """

        await self.__aio_session.close()


    async def __aenter__(self) -> Self:
        return self


    async def __aexit__(self,
                        _exc_type: Optional[type[BaseException]],
                        _exc_val: Optional[BaseException],
                        _exc_tb: Optional[TracebackType]) -> None:
        await self.close()


    async def request(self,
                      method: str,
                      endpoint: "UrlLike",
                      *,
                      base_url: UrlType=UrlType.API,
                      api_version: Optional[APIVersion]=APIVersion.V1,
                      **kwargs) -> "ClientResponse":
        """
        Overcharges the request to include the session cookie.

        :param method: The HTTP method to use.
        :param endpoint: The endpoint to map to.
        :param base_url: The root URL to use.
        :param api_version: The internal version of the API to use for the endpoints, defaults to :attr:`APIVersion.V1`

        :type method: :class:`str`
        :type endpoint: :type:`.UrlLike`
        :type base_url: Optional[:class:`.UrlType`]
        :type api_version: Optional[:class:`.APIVersion`]

        :return: The HTTP response.
        :rtype: `ClientResponse <https://docs.aiohttp.org/en/v3.11.13/client_reference.html#aiohttp.ClientResponse>`_
        """

        return await request(method,
                             endpoint,
                             base_url=base_url,
                             api_version=api_version,
                             session=self.__aio_session,
                             **kwargs)


    async def get(self,
                  endpoint: "UrlLike",
                  *,
                  params=None,
                  base_url: UrlType=UrlType.API,
                  api_version: Optional[APIVersion]=APIVersion.V1,
                  **kwargs) -> "ClientResponse":
        """
        Overcharges a GET request.

        :param endpoint: The endpoint to map to.
        :param params: A ``dict`` with the parameters of the request. Usually of type ``dict[str, int | str | None]``
        :param base_url: The root URL to use.
        :param api_version: The internal version of the API to use for the endpoints, defaults to :attr:`APIVersion.V1`

        :type endpoint: :type:`.UrlLike`
        :type params: Optional[:class:`dict`]
        :type base_url: Optional[:class:`.UrlType`]
        :type api_version: Optional[:class:`.APIVersion`]

        :return: The HTTP response.
        :rtype: `ClientResponse <https://docs.aiohttp.org/en/v3.11.13/client_reference.html#aiohttp.ClientResponse>`_
        """

        return await get(endpoint,
                         params=params,
                         base_url=base_url,
                         api_version=api_version,
                         session=self.__aio_session,
                         **kwargs)


    async def options(self,
                      endpoint: "UrlLike",
                      *,
                      base_url: UrlType=UrlType.API,
                      api_version: Optional[APIVersion]=APIVersion.V1,
                      **kwargs) -> "ClientResponse":
        """
        Overcharges an OPTIONS request.

        :param endpoint: The endpoint to map to.
        :param base_url: The root URL to use.
        :param api_version: The internal version of the API to use for the endpoints, defaults to :attr:`APIVersion.V1`

        :type endpoint: :type:`.UrlLike`
        :type base_url: Optional[:class:`.UrlType`]
        :type api_version: Optional[:class:`.APIVersion`]

        :return: The HTTP response.
        :rtype: `ClientResponse <https://docs.aiohttp.org/en/v3.11.13/client_reference.html#aiohttp.ClientResponse>`_
        """

        return await options(endpoint,
                             base_url=base_url,
                             api_version=api_version,
                             session=self.__aio_session,
                             **kwargs)


    async def head(self,
                   endpoint: "UrlLike",
                   *,
                   base_url: UrlType=UrlType.API,
                   api_version: Optional[APIVersion]=APIVersion.V1,
                   **kwargs) -> "ClientResponse":
        """
        Overcharges a HEAD request.

        :param endpoint: The endpoint to map to.
        :param base_url: The root URL to use.
        :param api_version: The internal version of the API to use for the endpoints, defaults to :attr:`APIVersion.V1`

        :type endpoint: :type:`.UrlLike`
        :type base_url: Optional[:class:`.UrlType`]
        :type api_version: Optional[:class:`.APIVersion`]

        :return: The HTTP response.
        :rtype: `ClientResponse <https://docs.aiohttp.org/en/v3.11.13/client_reference.html#aiohttp.ClientResponse>`_
        """

        return await head(endpoint,
                          base_url=base_url,
                          api_version=api_version,
                          session=self.__aio_session,
                          **kwargs)


    async def post(self,
                   endpoint: "UrlLike",
                   *,
                   data=None,
                   json=None,
                   base_url: UrlType=UrlType.API,
                   api_version: Optional[APIVersion]=APIVersion.V1,
                   **kwargs) -> "ClientResponse":
        """
        Overcharges a POST request.

        .. warning:: ``data`` and ``json`` cannot be used both at once.
        
        :param endpoint: The endpoint to map to.
        :param data: Dictionary, list of file-like object to send in the body of the request.
        :param json: JSON-like to send in the body of the request.
        :param base_url: The root URL to use.
        :param api_version: The internal version of the API to use for the endpoints, defaults to :attr:`APIVersion.V1`

        :type endpoint: :type:`.UrlLike`
        :type data: Optional[:class:`Any`]
        :type json: Optional[:class:`dict`]
        :type base_url: Optional[:class:`.UrlType`]
        :type api_version: Optional[:class:`.APIVersion`]

        :return: The HTTP response.
        :rtype: `ClientResponse <https://docs.aiohttp.org/en/v3.11.13/client_reference.html#aiohttp.ClientResponse>`_
        """

        return await post(endpoint,
                          data=data,
                          json=json,
                          base_url=base_url,
                          api_version=api_version,
                          session=self.__aio_session,
                          **kwargs)


    async def put(self,
                  endpoint: "UrlLike",
                  *,
                  data=None,
                  json=None,
                  base_url: UrlType=UrlType.API,
                  api_version: Optional[APIVersion]=APIVersion.V1,
                  **kwargs) -> "ClientResponse":
        """
        Overcharges a PUT request.

        .. warning:: ``data`` and ``json`` cannot be used both at once.

        :param endpoint: The endpoint to map to.
        :param data: Dictionary, list of file-like object to send in the body of the request, defaults to ``None``
        :param json: JSON-like to send in the body of the request, defaults to ``None``.
        :param base_url: The root URL to use.
        :param api_version: The internal version of the API to use for the endpoints, defaults to :attr:`APIVersion.V1`

        :type endpoint: :type:`.UrlLike`
        :type data: Optional[:class:`Any`]
        :type json: Optional[:class:`dict`]
        :type base_url: Optional[:class:`.UrlType`]
        :type api_version: Optional[:class:`.APIVersion`]

        :return: The HTTP response.
        :rtype: `ClientResponse <https://docs.aiohttp.org/en/v3.11.13/client_reference.html#aiohttp.ClientResponse>`_
        """

        return await put(endpoint,
                         data=data,
                         json=json,
                         base_url=base_url,
                         api_version=api_version,
                         session=self.__aio_session,
                         **kwargs)


    async def patch(self,
                    endpoint: "UrlLike",
                    *,
                    data=None,
                    json=None,
                    base_url: UrlType=UrlType.API,
                    api_version: Optional[APIVersion]=APIVersion.V1,
                    **kwargs) -> "ClientResponse":
        """
        Overcharges a PATCH request.

        .. warning:: ``data`` and ``json`` cannot be used both at once.

        :param endpoint: The endpoint to map to.
        :param data: Dictionary, list of file-like object to send in the body of the request, defaults to ``None``
        :param json: JSON-like to send in the body of the request, defaults to ``None``.
        :param base_url: The root URL to use.
        :param api_version: The internal version of the API to use for the endpoints, defaults to :attr:`APIVersion.V1`

        :type endpoint: :type:`.UrlLike`
        :type data: Optional[:class:`Any`]
        :type json: Optional[:class:`dict`]
        :type base_url: Optional[:class:`.UrlType`]
        :type api_version: Optional[:class:`.APIVersion`]

        :return: The HTTP response.
        :rtype: `ClientResponse <https://docs.aiohttp.org/en/v3.11.13/client_reference.html#aiohttp.ClientResponse>`_
        """

        return await patch(endpoint,
                           data=data,
                           json=json,
                           base_url=base_url,
                           api_version=api_version,
                           session=self.__aio_session,
                           **kwargs)


    async def delete(self,
                     endpoint: "UrlLike",
                     *,
                     base_url: UrlType=UrlType.API,
                     api_version: Optional[APIVersion]=APIVersion.V1,
                     **kwargs) -> "ClientResponse":
        """
        Overcharges a DELETE request.
        
        :param endpoint: The endpoint to map to.
        :param base_url: The root URL to use.
        :param api_version: The internal version of the API to use for the endpoints, defaults to :attr:`APIVersion.V1`

        :type endpoint: :type:`.UrlLike`
        :type base_url: Optional[:class:`.UrlType`]
        :type api_version: Optional[:class:`.APIVersion`]

        :return: The HTTP response.
        :rtype: `ClientResponse <https://docs.aiohttp.org/en/v3.11.13/client_reference.html#aiohttp.ClientResponse>`_
        """

        return await delete(endpoint,
                            base_url=base_url,
                            api_version=api_version,
                            session=self.__aio_session,
                            **kwargs)


    def set_session_cookie(self, cookie_auth: TokenValue) -> None:
        """
        :param cookie_auth: The new session cookie.

        :type cookie_auth: :type:`.TokenValue`
        """

        self.__aio_session.cookie_jar.update_cookies({"session": str(cookie_auth)}, response_url=SITE_DOMAIN)
