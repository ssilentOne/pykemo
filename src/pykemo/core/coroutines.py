"""
Asynchronous routines module.

Note that this modules focuses on ``asyncio`` coroutines, instead of ``gevent``'s unsent requests.
"""

from typing import TYPE_CHECKING, Optional

from requests import Session

from .request import UrlType, delete, get, post

if TYPE_CHECKING:
    from requests import Response

    from .request import UrlLike


async def co_get(endpoint: "UrlLike",
                 params=None,
                 url_type: UrlType=UrlType.API,
                 session: Optional[Session]=None,
                 **kwargs) -> "Response":
    """
    An awaitable wrapper for :meth:`.get()`.

    :param endpoint: The endpoint to map to.
    :param params: A ``dict`` with the parameters of the request. Usually of type ``dict[str, int | str | None]``
    :param url_type: The root URL to use.
    :param session: The session to use. If not provided, it will use a generic one.

    :type endpoint: :type:`.UrlLike`
    :type params: Optional[:class:`dict`]
    :type url_type: Optional[:class:`.UrlType`]
    :type session: Optional[`Session <https://requests.readthedocs.io/en/latest/api/#requests.Session>`_]

    :return: The HTTP response.
    :rtype: `Response <https://requests.readthedocs.io/en/latest/api/#requests.Response>`_
    """

    return get(endpoint, params, url_type, session, **kwargs)


async def co_post(endpoint: "UrlLike",
                  data=None,
                  json=None,
                  url_type: UrlType=UrlType.API,
                  session: Optional[Session]=None,
                  **kwargs) -> "Response":
    """
    An awaitable wrapper for :meth:`.post()`.
    
    :param endpoint: The endpoint to map to.
    :param data: Dictionary, list of file-like object to send in the body of the request.
    :param json: JSON-like to send in the body of the request.
    :param url_type: The root URL to use.
    :param session: The session to use. If not provided, it will use a generic one.

    :type endpoint: :type:`.UrlLike`
    :type data: Optional[:class:`Any`]
    :type json: Optional[:class:`dict`]
    :type url_type: Optional[:class:`.UrlType`]
    :type session: Optional[`Session <https://requests.readthedocs.io/en/latest/api/#requests.Session>`_]

    :return: The HTTP response.
    :rtype: `Response <https://requests.readthedocs.io/en/latest/api/#requests.Response>`_
    """

    return post(endpoint, data, json, url_type, session, **kwargs)


async def co_delete(endpoint: "UrlLike",
                    url_type: UrlType=UrlType.API,
                    session: Optional[Session]=None,
                    **kwargs) -> "Response":
    """
    An awaitable wrapper for :meth:`.delete()`.
    
    :param endpoint: The endpoint to map to.
    :param url_type: The root URL to use.
    :param session: The session to use. If not provided, it will use a generic one.

    :type endpoint: :type:`.UrlLike`
    :type url_type: Optional[:class:`.UrlType`]
    :type session: Optional[`Session <https://requests.readthedocs.io/en/latest/api/#requests.Session>`_]

    :return: The HTTP response.
    :rtype: `Response <https://requests.readthedocs.io/en/latest/api/#requests.Response>`_
    """

    return delete(endpoint, url_type, session, **kwargs)
