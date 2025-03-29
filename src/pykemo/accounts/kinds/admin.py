"""
Administrator account module.
"""

from asyncio import gather
from typing import TYPE_CHECKING, Iterable, Optional

from ...exceptions import InsufficientPrivileges
from ..base import _AccountBase, _AccountParams
from ..role import AccountRole
from ..view import AccountView
from .cons import _ConsumerMixin
from .mod import _ModeratorMixin

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


    async def view_accounts(self,
                            *,
                            name: Optional[str]=None,
                            role: Optional[AccountRole]=None,
                            page: Optional[int]=None,
                            limit: Optional[int]=None) -> list[AccountView]:
        """
        Tries to fetch accounts with minimal info, unlike the ones that manage their own session.
        
        :param name: An account name to filter results by, defaults to ``None``
        :param role: An account role type to filter results by, defaults to ``None``
        :param page: A value for paging in account view retrieving, defaults to ``None``
        :param limit: A value for fetching limiting in account view retrieving, defaults to ``None``
        
        :type name: :class:`str`, optional
        :type role: :class:`.AccountRole`, optional
        :type page: :class:`int`, optional
        :type limit: :class:`int`, optional

        :raises ValueError: If ``page`` or ``limit`` are present and any of them has value 0 or less.
        :raises InsufficientPrivileges: If, somehow, the one invoking this operation isn`t at least an administrator.
        
        :return: A list of simplified account views, if found.
        :rtype: list[:class:`.AccountView`]
        """

        if page is not None and page <= 0:
            raise ValueError(f"'page' must be a positive integer but value {page} was found")

        if limit is not None and limit <= 0:
            raise ValueError(f"'limit' must be a positive integer but value {limit} was found")

        params = {}
        if name is not None:
            params.update(name=name)

        if role is not None:
            params.update(role=role)

        if page is not None:
            params.update(page=page)

        if limit is not None:
            params.update(limit=limit)

        res = await self.session.get("/account/administrator/accounts", params=params)
        body = await res.json()

        if res.status == 404:
            raise InsufficientPrivileges(body.get(
                "error", "Insufficient privileges for this operation")
            )

        if res.status != 200:
            return []

        views_tasks = []
        for acc_fields in body.get("accounts"):
            views_tasks.append(AccountView.from_dict(**acc_fields))

        return await gather(*views_tasks)


    async def change_roles(self,
                           mod_ids: Iterable["CreatorID"],
                           cons_ids: Iterable["CreatorID"]) -> bool:
        """
        _summary_
        
        :param mod_ids: The IDs of the soon to-be moderators.
        :param cons_ids: The IDs of the soon to-be consumers.

        :type mod_ids: Iterable[:type:`.CreatorID`]
        :type cons_ids: Iterable[:type:`.CreatorID`]

        :raises InsufficientPrivileges: If, somehow, the one invoking this operation isn`t at least an administrator.

        :return: A boolean value indicating if the operation was a success.
        :rtype: :class:`bool`
        """

        res = await self.session.post(
            "/account/administrator/accounts",
            json={
                "moderator": list(mod_ids),
                "consumer": list(cons_ids)
            }
        )

        if res.status == 404:
            raise InsufficientPrivileges((await res.json()).get(
                "error", "Insufficient privileges for this operation")
            )

        return res.status == 200


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
