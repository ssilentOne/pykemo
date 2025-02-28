"""
Kemono session module.
"""

from typing import TYPE_CHECKING

from requests import Session
from requests.adapters import HTTPAdapter, Retry

from ..core import ADAPTER_PREFIX, BACKOFF_FACTOR, FORCELIST, MAX_RETRIES

if TYPE_CHECKING:
    from requests import Response


class KemoSession(Session):
    """
    Kemono session.
    """

    def __init__(self, cookie_auth: str) -> None:
        """
        Initializes the instance with custom adapters.

        :param cookie_auth: The session cookie that can be found after a successful login.
                            Pykemo cannot find this on its own, the user must provide it.

        :type cookie_auth: :class:`str`
        """

        super().__init__()
        self.mount(ADAPTER_PREFIX, HTTPAdapter(max_retries=Retry(total=MAX_RETRIES,
                                                                 backoff_factor=BACKOFF_FACTOR,
                                                                 status_forcelist=FORCELIST)))

        self.session_cookie: str = cookie_auth


    def request(self, *args, **kwargs) -> "Response":
        """
        Overcharges the request to include the session cookie.
        """

        kwargs.update(cookies={"session": self.session_cookie})
        return super().request(*args, **kwargs)



    def set_session_cookie(self, cookie_auth: str) -> None:
        """
        :param cookie_auth: The new session cookie.

        :type cookie_auth: :class:`str`
        """

        self.session_cookie: str = cookie_auth
