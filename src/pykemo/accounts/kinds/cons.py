"""
Consumer account module.
"""

from asyncio import gather
from typing import TYPE_CHECKING, Optional

from ..._aux import add_session_to_post
from ...creators import Creator, CreatorsList
from ...exceptions import PyKemoException
from ...posts import Post, PostsList
from ..base import _AccountBase, _AccountParams
from ..role import AccountRole

if TYPE_CHECKING:
    from ...posts import PostID
    from ...services import ServiceLike


class _ConsumerMixin(_AccountParams):
    "A basic compound of all consumer level operations."

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


    async def get_post(self,
                       service: "ServiceLike",
                       post_id: "PostID") -> Optional[Post]:
        """
        Wrapper for fetching a post without the creator ID.
        
        :param service: The service the post falls under.
        :param post_id: The ID of the specific post.
        
        :type service: :type:`.ServiceLike`
        :type post_id: :type:`.PostID`
        
        :return: The loaded post, if it was found. If not, returns ``None``.
        :rtype: Optional[:class:`.Post`]
        """

        res = await self.session.get(f"/{service}/post/{post_id}")

        if res.status == 404:
            return None

        creator_id = (await res.json()).get("artist_id")
        creator = await self.get_creator(service, creator_id)

        return await creator.get_post(post_id)


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


class Consumer(_AccountBase, _ConsumerMixin):
    """
    A basic consumer account.

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
        return AccountRole.CONSUMER
