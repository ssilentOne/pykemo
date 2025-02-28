"""
Account module.
"""

from ..core import get
from ..creators import Creator, CreatorsList
from ..posts import Post, PostsList
from .session import KemoSession


class Account:
    """
    A Kemono account. A session token is provided, and is used to send requests with
    user authentication.
    """

    def __init__(self, token: str) -> None:
        """
        Initializes an instance with a session token.

        :param token: The session token. Can be found in the response cookies after
                      a sucessful login.

        :type token: :class:`str`
        """

        self.session: KemoSession = KemoSession(token)


    def __enter__(self) -> "Account":
        """
        Enters the context of this type with the ``with`` statement.

        :return: This very instance, to be used in the context.
        :rtype: :class:`.Account`
        """

        return self


    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """
        Exits the context of the type.
        """

        self.logout()


    @property
    def token(self) -> str:
        """
        :returns: The session token.
        :rtype: :class:`str`
        """

        return self.session.session_cookie


    def logout(self) -> None:
        """
        Log out of the session.
        """

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
