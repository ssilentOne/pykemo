"""
Administrator account module.
"""

from typing import TYPE_CHECKING

from ...exceptions import InsufficientPrivileges
from ..base import _AccountBase, _AccountParams
from .cons import _ConsumerMixin
from .mod import _ModeratorMixin
from ..role import AccountRole

if TYPE_CHECKING:
    from ...creators import Creator, CreatorID
    from ...services import ServiceLike


class _AdministratorMixin(_AccountParams):
    "A basic compound of all moderator level operations."

    async def remove_creator_link(self, service: "ServiceLike", creator_id: "CreatorID") -> bool:
        """
        Removes a creator from its linked accounts. This is useful when when dealing with
        wrongful linkage where creators linked are not acutally the same person.
        This one uses only the service and ID, without loading a creator.

        :param service: The service of the creator in question.
        :param creator_id: The ID of the creator to separate from the other links.

        :type service: :type:`.ServiceLike`
        :type creator_id: :type:`.CreatorID`

        :raises InsufficientPrivileges: If, somehow, the one invoking this operation isn`t at
                                        least an administrator.

        :return: A boolean value indicating if the operation was successful or not.
        :rtype: :class:`bool`
        """

        res = await self.session.delete(f"/{service}/user/{creator_id}/links")

        if res.status == 404:
            raise InsufficientPrivileges((await res.json()).get(
                "error", "Insufficient privileges for this operation")
            )

        return res.status == 204


    async def remove_creator(self, creator: "Creator") -> bool:
        """
        Removes a creator from its linked accounts. This is useful when when dealing with
        wrongful linkage where creators linked are not acutally the same person.
        
        :param creator: The creator to separate from the other links.
        
        :type creator: :class:`.Creator`

        :raises InsufficientPrivileges: If, somehow, the one invoking this operation isn`t at least an administrator.

        :return: A boolean value indicating if the operation was successful or not.
        :rtype: :class:`bool`
        """

        return await self.remove_creator_link(creator.id, creator.service)


class Admin(_AccountBase, _ConsumerMixin, _ModeratorMixin, _AdministratorMixin):
    """
    An administrator account.

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
        return AccountRole.ADMINISTRATOR
