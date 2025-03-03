"""
Kemono session module.
"""

from typing import TYPE_CHECKING, TypeAlias

from requests import Session
from requests.adapters import HTTPAdapter, Retry

from ..core import (
    ADAPTER_PREFIX,
    BACKOFF_FACTOR,
    FORCELIST,
    MAX_RETRIES,
    UrlType,
    delete,
    get,
    post,
    request,
)

if TYPE_CHECKING:
    from requests import Response

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

        self.__session = Session()
        self.__session.mount(ADAPTER_PREFIX, HTTPAdapter(max_retries=Retry(total=MAX_RETRIES,
                                                                 backoff_factor=BACKOFF_FACTOR,
                                                                 status_forcelist=FORCELIST)))


    @classmethod
    def with_token(cls, cookie_auth: TokenValue) -> "KemoSession":
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


    def __enter__(self) -> "KemoSession":
        """
        Enters the context of this session with the ``with`` statement.

        :return: This very instance, to be used in the context.
        :rtype: :class:`.KemoSession`
        """

        return self.__session.__enter__()


    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """
        Exits the context of the session.
        """

        self.__session.__exit__(exc_type, exc_value, traceback)


    def close(self) -> None:
        """
        Wrapper for closing the session.
        """

        self.__session.close()


    def request(self,
                method: str,
                endpoint: "UrlLike",
                url_type: UrlType=UrlType.API,
                **kwargs) -> "Response":
        """
        Overcharges the request to include the session cookie.

        :param method: The HTTP method to use.
        :param endpoint: The endpoint to map to.
        :param url_type: The root URL to use.

        :type method: :class:`str`
        :type endpoint: :type:`.UrlLike`
        :type url_type: Optional[:class:`.UrlType`]

        :return: The HTTP response.
        :rtype: `Response <https://requests.readthedocs.io/en/latest/api/#requests.Response>`_
        """

        return request(method, endpoint, url_type, session=self.__session, **kwargs)


    def get(self,
            endpoint: "UrlLike",
            params=None,
            url_type: UrlType=UrlType.API,
            **kwargs) -> "Response":
        """
        Overcharges a GET request.

        :param endpoint: The endpoint to map to.
        :param params: A ``dict`` with the parameters of the request. Usually of type ``dict[str, int | str | None]``
        :param url_type: The root URL to use.

        :type endpoint: :type:`.UrlLike`
        :type params: Optional[:class:`dict`]
        :type url_type: Optional[:class:`.UrlType`]

        :return: The HTTP response.
        :rtype: `Response <https://requests.readthedocs.io/en/latest/api/#requests.Response>`_
        """

        return get(endpoint, params, url_type, session=self.__session, **kwargs)


    def post(self,
             endpoint: "UrlLike",
             data=None,
             json=None,
             url_type: UrlType=UrlType.API,
             **kwargs) -> "Response":
        """
        Overcharges a POST request.
        
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

        return post(endpoint, data, json, url_type, session=self.__session, **kwargs)


    def delete(self,
               endpoint: "UrlLike",
               url_type: UrlType=UrlType.API,
               **kwargs) -> "Response":
        """
        Overcharges a DELETE request.
        
        :param endpoint: The endpoint to map to.
        :param url_type: The root URL to use.

        :type endpoint: :type:`.UrlLike`
        :type url_type: Optional[:class:`.UrlType`]

        :return: The HTTP response.
        :rtype: `Response <https://requests.readthedocs.io/en/latest/api/#requests.Response>`_
        """

        return delete(endpoint, url_type, session=self.__session, **kwargs)


    def set_session_cookie(self, cookie_auth: TokenValue) -> None:
        """
        :param cookie_auth: The new session cookie.

        :type cookie_auth: :type:`.TokenValue`
        """

        self.__session.cookies.set("session", str(cookie_auth), domain=SITE_DOMAIN)
