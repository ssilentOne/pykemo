"""
Account module.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal, TypeAlias, Union

from .._aux import MILI_DATE_FMT
from ..core import get
from ..creators import Creator, CreatorsList
from ..exceptions import AlreadyLoggedIn, InvalidLogin, LoginError
from ..posts import Post, PostsList
from ..sessions import KemoSession
from .role import AccountRole

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


    def __enter__(self) -> "Account":
        """
        Enters the context of this account with the ``with`` statement.

        :return: This very instance, to be used in the context.
        :rtype: :class:`.Account`
        """

        return self


    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """
        Exits the context of the type.
        """

        self.logout(close_session=False) # the method below is better for closing the session
        self.session.__exit__(exc_type, exc_value, traceback)


    @classmethod
    def login(cls,
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
        login_res = session.post("/authentication/login", json=dict(username=user, password=password))

        # invalid due to user errors
        if login_res.status_code == 400:
            session.__exit__()
            raise InvalidLogin(login_res.json.get("error", "The login is invalid due to user errors"))

        # already logged in
        elif login_res.status_code == 409:
            session.__exit__()
            raise AlreadyLoggedIn(login_res.json.get("error", "The user is already logged in"))

        # another unknown error
        elif login_res.status_code != 200:
            session.__exit__()
            raise LoginError(login_res.json.get("error", "An unexpected error ocurred during the login"))

        # at this point the session instance already has the session cookie inside
        account_data = login_res.json()
        return cls(
            id=account_data.get("id"),
            username=account_data.get("username"),
            created_at=datetime.strptime(account_data.get("created_at"), MILI_DATE_FMT),
            role=AccountRole(account_data.get("role")),
            session=session
        )


    def logout(self, close_session: bool=True) -> None:
        """
        Log out of the session.
        
        :param close_session: If to also close the underlying session instance., defaults to `True`
        
        :type close_session: :class:`bool`, optional
        """

        self.session.post("/authentication/logout")
        if close_session:
            self.session.close()


    def favorite_artists(self) -> CreatorsList:
        """
        Tries to retrieve this account's favorite artists.
        Alias for :meth:`.favorite_creators()`.

        :return: The list of favorite artists (creators).
        :rtype: list[:class:`.Creator`]
        """

        return self.favorite_creators()


    def favorite_creators(self) -> CreatorsList:
        """
        Tries to retrieve this account's favorite creators.

        :return: The list of favorite creators.
        :rtype: list[:class:`.Creator`]
        """

        res = get("/account/favorites", params={"type": "artist"}, session=self.session)
        creators = []

        for creator_fields in res.json():
            creators.append(Creator.from_profile(creator_fields.get("service"),
                                                 creator_fields.get("id")))

        return creators


    def favorite_posts(self) -> PostsList:
        """
        Tries to retrieve this account's favorite posts.

        :return: The list of favorite posts.
        :rtype: list[:class:`.Post`]
        """

        res = get("/account/favorites", params={"type": "post"}, session=self.session)
        posts = []

        for post_fields in res.json():
            posts.append(Post.from_dict(**post_fields))

        return posts
