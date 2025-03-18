"""
Account module.
"""

from asyncio import gather
from dataclasses import dataclass, field
from datetime import datetime
from types import TracebackType
from typing import TYPE_CHECKING, Literal, Optional, TypeAlias, Union

from .._aux import MILI_DATE_FMT, add_session_to_post
from ..creators import Creator, CreatorsList
from ..exceptions import (
    AlreadyLoggedIn,
    InvalidLogin,
    InvalidRegister,
    LoginError,
    PyKemoException,
    RegisterError,
)
from ..posts import Post, PostsList
from ..sessions import KemoSession
from .role import AccountRole

if TYPE_CHECKING:
    from ..services import ServiceLike

_AccountFields: TypeAlias = Literal["id", "username", "created_at", "role"]
AccountDict: TypeAlias = dict[_AccountFields, Union[int, str, None]]


@dataclass(kw_only=True)
class Account:
    """
    A Kemono account.

    .. warning:: It is not recommended to use unless you know what you're doing. Methods like :meth:`.login()` are preferred as they automatically create a session internally.
    
    :param id: The account ID.
    :param username: The name of the user's account.
    :param created_at: When was the account created.
    :param role: The special role/rank of the account.
    :param session: The underlying session of the account context.

    :type id: :class:`int`
    :type username: :class:`str`
    :type created_at: :class:`datetime.datetime`
    :type role: :class:`.AccountRole`
    :type session: :class:`.KemoSession`
    """

    id: int
    username: str
    created_at: datetime = field(repr=False)
    role: AccountRole
    session: KemoSession = field(repr=False)


    async def __aenter__(self) -> "Account":
        """
        Enters the context of this account with the ``with`` statement.

        :return: This very instance, to be used in the context.
        :rtype: :class:`.Account`
        """

        return self


    async def __aexit__(self,
                        _exc_type: Optional[type[BaseException]],
                        _exc_val: Optional[BaseException],
                        _exc_tb: Optional[TracebackType]) -> None:
        """
        Exits the context of the type.
        """

        await self.logout()


    @classmethod
    async def login(cls,
                    user: str,
                    password: str) -> "Account":
        """
        Tries to login with a given user and password.
        
        :param user: The username to try to login with.
        :param password: The password to try to login with.
  
        :type user: :class:`str`
        :type password: :class:`str`

        :raises InvalidLogin: The login had incorrect data.
        :raises AlreadyLoggedIn: The user is already logged in.
        :raises LoginError: Another error ocurred.
        
        :return: The account of the user, if sucessfully logged in.
        :rtype: :class:`.Account`
        """     

        session = KemoSession()
        login_res = await session.post("/authentication/login", json=dict(username=user, password=password))
        res_json = await login_res.json()

        # invalid due to user errors
        if login_res.status == 400:
            session.close()
            raise InvalidLogin(res_json.get("error", "The login is invalid due to user errors"))

        # already logged in
        elif login_res.status == 409:
            session.close()
            raise AlreadyLoggedIn(res_json.get("error", "The user is already logged in"))

        # another unknown error
        elif login_res.status != 200:
            session.close()
            raise LoginError(res_json.get("error", "An unexpected error ocurred during the login"))

        # at this point the session instance already has the session cookie inside
        return cls(
            id=res_json.get("id"),
            username=res_json.get("username"),
            created_at=datetime.strptime(res_json.get("created_at"), MILI_DATE_FMT),
            role=AccountRole(res_json.get("role")),
            session=session
        )


    @classmethod
    async def register(cls,
                       user: str,
                       password: str) -> "Account":
        """
        Tries to register a accountuser.
        
        :param user: The username to try to register with.
        :param password: The password to try to register with.
  
        :type user: :class:`str`
        :type password: :class:`str`

        :raises InvalidRegister: Failed to register due to user errors.
        :raises RegisterError: Another error ocurred.
        
        :return: The account of the user, if sucessfully logged in after registering.
        :rtype: :class:`.Account`
        """

        session = KemoSession()
        register_res = await session.post("/authentication/register",
                                          json=dict(username=user, password=password,
                                                    confirm_password=password, favorites_json=""))

        # invalid due to user errors
        if register_res.status == 400:
            session.close()
            raise InvalidRegister((await register_res.json()).get("error", "The process was invalidated due to user error."))

        # an unknown error
        elif register_res.status != 200:
            session.close()
            raise RegisterError((await register_res.json()).get("error", "An unexpected error ocurred in the registering process."))

        login_body = await (await session.post("/authentication/login", json=dict(username=user, password=password))).json()

        return cls(
            id=login_body.get("id"),
            username=login_body.get("username"),
            created_at=datetime.strptime(login_body.get("created_at"), MILI_DATE_FMT),
            role=AccountRole(login_body.get("role")),
            session=session
        )


    async def logout(self) -> None:
        """
        Log out of the session.
        """

        await self.session.post("/authentication/logout")
        await self.session.close()


    async def change_password(self,
                              current_password: str,
                              new_password: str,
                              close_on_fail: bool=True) -> None:
        """
        Attempts to change the current password for this account.

        .. warning:: `Be careful.` If this launches an exception and ``close_on_fail`` is set to
                     ``False``, the internal session will not close. It's the responsability of
                     the programmer at this point to close it if that happens.
        
        :param current_password: The password that is already set.
        :param new_password: The new value to overwrite the current password with.
        :param close_on_fail: Wether to close the internal session if this launches an exception, defaults to ``True``.
        
        :type current_password: :class:`str`
        :type new_password: :class:`str`
        :type close_on_fail: :class:`bool`, optional

        :raises PyKemoException: If the change fails for whatever reason.
        """

        request_body = {
            "current-password": current_password,
            "new-password": new_password,
            "new-password-confirmation": new_password
        }
        change_res = await self.session.post("/account/change_password",
                                             json=request_body)

        if change_res.status == 200:
            return

        if close_on_fail:
            self.logout()

        raise PyKemoException((await change_res.json()).get("error", "An unexpected error ocurred in the password change."))


    async def favorite_artists(self) -> CreatorsList:
        """
        Tries to retrieve this account's favorite artists.
        Alias for :meth:`.favorite_creators()`.

        :return: The list of favorite artists (creators).
        :rtype: list[:class:`.Creator`]
        """

        return await self.favorite_creators()


    async def favorite_creators(self) -> CreatorsList:
        """
        Tries to retrieve this account's favorite creators.

        :return: The list of favorite creators.
        :rtype: list[:class:`.Creator`]
        """

        res = await self.session.get("/account/favorites", params={"type": "artist"})
        creator_tasks = []

        async for creator_fields in res.json():
            creator_tasks.append(self.get_creator(creator_fields.get("service"),
                                                  creator_fields.get("id")))

        return await gather(*creator_tasks)


    async def favorite_posts(self) -> PostsList:
        """
        Tries to retrieve this account's favorite posts.

        :return: The list of favorite posts.
        :rtype: list[:class:`.Post`]
        """

        res = await self.session.get("/account/favorites", params={"type": "post"})
        posts_tasks = []

        async for post_fields in res.json():
            posts_tasks.append(add_session_to_post(Post.from_dict(**post_fields), self.session))

        return await gather(*posts_tasks)


    async def get_creator(self, service: "ServiceLike", creator_id: str) -> Optional[Creator]:
        """
        A wrapper for fetching a creator with the account session.

        :param service: The service of the creator.
        :param creator_id: The ID of the creator.

        :type service: :type:`.ServiceLike`
        :type creator_Id: :class:`str`

        :return: The creator instance, if found. Otherwise returns ``None``.
        :rtype: Optional[:class:`.Creator`]
        """

        return await Creator.from_profile(service, creator_id, self.session)


    async def random_creator(self) -> Optional[Creator]:
        """
        Wrapper for retrieving a random creator from the site.

        :return: If a creator is found, retrieve and create a :class:`Creator` instance, otherwise return ``None``.
        :rtype: Optional[:class:`Creator`]
        """

        return await Creator.random(session=self.session)


    async def random_post(self) -> Optional[Post]:
        """
        Wrapper for retrieving a random post from the site.

        :return: If a creator is found, retrieve and create a :class:`.Post` instance, otherwise return ``None``.
        :rtype: Optional[:class:`.Post`]
        """

        post_res = await self.session.get("/posts/random")

        if post_res.status != 200:
            return None

        post_fields = await post_res.json()
        service = post_fields.get('service')
        creator_id = post_fields.get('artist_id')

        post_exists = await self.session.get(f"/{service}/user/{creator_id}/post/{post_fields.get('post_id')}")

        if post_exists.status == 404:
            return None

        fields = (await post_exists.json()).get("post")
        fields.update(creator=(await self.get_creator(service, creator_id)))

        return await add_session_to_post(Post.from_dict(**fields), self.session)
