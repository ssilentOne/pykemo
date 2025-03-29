"""
Creator linkage requests.
"""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional, Self, TypeAlias

from ...creators import Creator
from .creator_lnk_status import CreatorLinkStatus

if TYPE_CHECKING:
    from ...core import UrlLike
    from ...sessions import KemoSession

CreatorLnkReqID: TypeAlias = int


@dataclass(kw_only=True)
class CreatorLinkRequest:
    """
    A request for two creators to be understood as the same person.

    .. warning:: This is NOT supposed to be used as-is. It is ideally only made through :meth:`Moderator.creator_requests()` .

    :param id: The ID of the request.
    :param from_creator: The creator from which to make the link.
    :param to_creator: The creator to which make the link.
    :param reason: The reason for making the link request, if any.
    :param requester_id: The ID of the requester's account.
    :param status: The status of the request.

    :type id: :type:`.CreatorLnkReqID`
    :type from_creator: :class:`.Creator`
    :type to_creator: :class:`.Creator`
    :type reason: :class:`str`
    :type requester_id: :class:`int`
    :type status: :class:`.CreatorLinkStatus`
    """

    id: CreatorLnkReqID
    from_creator: Creator = field(repr=False)
    to_creator: Creator = field(repr=False)
    reason: str = field(repr=False, default="")
    requester_id: int
    status: CreatorLinkStatus

    __kemo_session: Optional["KemoSession"] = field(init=False, repr=False, default=None)


    @classmethod
    async def from_dict(cls, **fields) -> Self:
        """
        Initializes an creator link request instance from a response fields.

        :return: An instace of a link request.
        :rtype: :class:`.CreatorLinkRequest`
        """

        stat = fields.get("status")
        status = (CreatorLinkStatus(stat)
                  if stat in CreatorLinkStatus else CreatorLinkStatus.OTHER)

        return cls(
            id=fields.get("id"),
            from_creator=await Creator.from_profile(
                fields.get("from_service"),
                fields.get("from_id")
            ),
            to_creator=await Creator.from_profile(
                fields.get("to_service"),
                fields.get("to_id")
            ),
            reason=fields.get("reason", ""),
            requester_id=fields.get("requester_id"),
            status=status
        )


    def pending(self) -> bool:
        """
        Checks if the link request is in a PENDING status.
        
        :return: Wether the link request is pending or not.
        :rtype: :class:`bool`
        """

        self.status == CreatorLinkStatus.PENDING


    def set_underlying_session(self, ks: "KemoSession") -> Self:
        """
        Quietly sets the session which the creator request uses for its requests.
        
        :param session: The session instance.
        
        :type session: :class:`.KemoSession`

        :return: The same instance of the request, for convenience.
        :rtype: :class:`.CreatorLinkRequest`
        """

        self.__kemo_session = ks
        return self


    async def _sucessful_lnk_check(self, endpoint: "UrlLike") -> bool:
        """
        Attemps to send a request and checks if the response is sucessful.
        
        :param endpoint: The endpoint to send the request to.
        
        :type endpoint: :class:`.UrlLike`
        
        :return: Wether the request was sucessful or not.
        :rtype: :class:`bool`
        """

        res = await self.__kemo_session.post(endpoint)

        if res.status != 200:
            return False

        self.status = CreatorLinkStatus.OTHER
        return True


    async def approve(self) -> bool:
        """
        Tries to approve the creator link request.
        
        :return: A boolean value, indicating wether it was sucessful in approving the
                 request or not.
        :rtype: :class:`bool`
        """

        return await self._sucessful_lnk_check(
            f"/account/moderator/creator_link_requests/{self.id}/approve"
        )


    async def reject(self) -> bool:
        """
        Tries to reject the creator link request.
        
        :return: A boolean value, indicating wether it was sucessful in rejecting the
                 request or not.
        :rtype: :class:`bool`
        """
    
        return await self._sucessful_lnk_check(
            f"/account/moderator/creator_link_requests/{self.id}/reject"
        )
