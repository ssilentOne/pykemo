"""
Moderator account module.
"""

from asyncio import gather
from collections.abc import Coroutine
from typing import Any

from ..moderation import CreatorLinkRequest
from ..exceptions import InsufficientPrivileges
from .base import _AccountBase, _AccountParams
from .cons import _ConsumerMixin
from .role import AccountRole


class _ModeratorMixin(_AccountParams):
    "A basic compound of all moderator level operations."

    async def creator_link_requests(self) -> list[CreatorLinkRequest]:
        """
        Fetches a list of creator link requests that have yet to be reviewed.

        :raises InsufficientPrivileges: If, somehow, the one invoking this operation isn`t at least
        a moderator.
        
        :return: A list of pending creator link requests, if any.
        :rtype: list[:class:`.CreatorLinkRequest`]
        """

        res = await self.session.get("/account/moderator/tasks/creator_links")
        body = await res.json()

        if res.status == 404:
             raise InsufficientPrivileges(body.get("error", "Insufficient privileges for this operation"))

        if res.status != 200:
            return []

        async def add_session_to_lnk_request(
                    lnk_req_task: Coroutine[Any, Any, CreatorLinkRequest]) -> CreatorLinkRequest:
                return (await lnk_req_task).set_underlying_session(self.session)

        link_tasks = []
        for lnk_fields in body:
            link_tasks.append(
                 add_session_to_lnk_request(CreatorLinkRequest.from_dict(**lnk_fields))
            )

        return await gather(*link_tasks)


class Moderator(_AccountBase, _ConsumerMixin, _ModeratorMixin):
    """
    A moderator account.

    .. warning:: It is not recommended to use unless you know what you're doing. Methods like :meth:`.login()` are preferred as they automatically create a session internally.
    
    :param id: The account ID.
    :param username: The name of the user's account.
    :param created_at: When was the account created.
    :param ks: The underlying session of the account context.

    :type id: :class:`int`
    :type username: :class:`str`
    :type created_at: :class:`datetime.datetime`
    :type ks: :class:`.KemoSession`
    """

    @staticmethod
    def role() -> AccountRole:
        return AccountRole.MODERATOR
