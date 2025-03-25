"""
Accounts abstract base module.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from types import TracebackType
from typing import Literal, Optional, Self, TypeAlias, Union

from .._aux import MILI_DATE_FMT
from ..exceptions import (
    AlreadyLoggedIn,
    InvalidLogin,
    InvalidRegister,
    InvalidRole,
    LoginError,
    RegisterError,
)
from ..sessions import KemoSession
from .role import AccountRole

_AccountFields: TypeAlias = Literal["id", "username", "created_at", "role"]
AccountDict: TypeAlias = dict[_AccountFields, Union[int, str, None]]


@dataclass(kw_only=True)
class _AccountParams:
    "The very basic initial parameters of an Account."

    id: int
    username: str
    created_at: datetime = field(repr=False)
    session: KemoSession = field(repr=False)


class _AccountBase(ABC, _AccountParams):
    """
    .. warning:: `This is intended for internal purposes.` Use subclasses instead.
    """

    @classmethod
    async def from_dict(cls, **fields) -> Self:
        """
        Initializes an Account instance from a response fields.

        :return: An instace of an account.
        :rtype: :class:`.CommentRevision`
        """

        ks_cand = fields.get("session", None)
        if ks_cand is None:
            ks_cand = KemoSession()

        return cls(
            id=fields.get("id"),
            username=fields.get("username"),
            created_at=datetime.strptime(fields.get("created_at"), MILI_DATE_FMT),
            session=ks_cand
        )


    @classmethod
    async def login(cls,
                    user: str,
                    password: str,
                    session: Optional[KemoSession]=None) -> Self:
        """
        Tries to login with a given user and password.
        
        :param user: The username to try to login with.
        :param password: The password to try to login with.
        :param session: The Kemono session to use, defaults to ``None``.
  
        :type user: :class:`str`
        :type password: :class:`str`
        :type session: :class:`.KemoSession`, optional

        :raises InvalidLogin: The login had incorrect data.
        :raises AlreadyLoggedIn: The user is already logged in.
        :raises LoginError: Another error ocurred.
        :raises InvalidRole: Another type of role was expected.
        
        :return: The account of the user, if sucessfully logged in.
        """

        session = (session if session is not None else KemoSession())
        res_json = await cls._get_login_res(user, password, session)

        res_json.update(session=session)
        return await cls.from_dict(**res_json)


    @classmethod
    async def register(cls,
                       user: str,
                       password: str) -> Self:
        """
        Tries to register a account user.
        
        :param user: The username to try to register with.
        :param password: The password to try to register with.
  
        :type user: :class:`str`
        :type password: :class:`str`

        :raises InvalidRegister: Failed to register due to user errors.
        :raises RegisterError: Another error ocurred.
        
        :return: The account of the user, if sucessfully logged in after registering.
        """

        session = KemoSession()
        await cls._get_reg_res(user, password, session)

        return await cls.login(user, password, session)


    async def __aenter__(self) -> Self:
        """
        Enters the context of this account with the ``with`` statement.

        :return: This very instance, to be used in the context.
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
    async def _get_login_res(cls,
                             user: str,
                             password: str,
                             session: KemoSession) -> AccountDict:
        """
        Tries to login, and returns the response body without further processing.
        
        :param user: The username to try to login with.
        :param password: The password to try to login with.
        :param session: The Kemono session to use.
  
        :type user: :class:`str`
        :type password: :class:`str`
        :type session: :class:`.KemoSession`

        :raises InvalidLogin: The login had incorrect data.
        :raises AlreadyLoggedIn: The user is already logged in.
        :raises LoginError: Another error ocurred.
        :raises InvalidRole: Another type of role was expected.
        
        :return: The body of the login response.
        :rtype: :type:`.AccountDict`
        """

        login_res = await session.post("/authentication/login", json=dict(username=user, password=password))
        res_json = await login_res.json()

        # invalid due to user errors
        if login_res.status == 400:
            session.close()
            raise InvalidLogin(res_json.get("error", "The login is invalid due to user errors"))

        # already logged in
        if login_res.status == 409:
            session.close()
            raise AlreadyLoggedIn(res_json.get("error", "The user is already logged in"))

        # another unknown error
        if login_res.status != 200:
            session.close()
            raise LoginError(res_json.get("error", "An unexpected error ocurred during the login"))

        role_name = res_json.get("role").lower()
        if AccountRole(role_name) is not cls.role():
            raise InvalidRole(res_json.get("error", f"A role of '{cls.role()}' was expected, found '{role_name}'."))

        # at this point the session instance already has the session cookie inside
        return res_json


    @classmethod
    async def _get_reg_res(cls,
                           user: str,
                           password: str,
                           session: KemoSession) -> None:
        """
        Tries to register, and returns the response body without further processing.
        
        :param user: The username to try to register with.
        :param password: The password to try to register with.
  
        :type user: :class:`str`
        :type password: :class:`str`

        :raises InvalidRegister: Failed to register due to user errors.
        :raises RegisterError: Another error ocurred.
        """

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


    @staticmethod
    @abstractmethod
    def role() -> AccountRole:
        """
        Tries to describe this account's rank.
        
        :return: The account role type.
        :rtype: :class:`.AccountRole`
        """

        raise NotImplementedError


    async def logout(self) -> None:
        """
        Log out of the session.
        """

        await self.session.post("/authentication/logout")
        await self.session.close()
