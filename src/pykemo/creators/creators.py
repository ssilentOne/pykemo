"""
Creators module.
"""

from asyncio import gather
from collections.abc import Coroutine
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any, Literal, Optional, TypeAlias, Union

from .._aux import (
    MILI_DATE_FMT,
    add_session_to_post,
    before_date,
    get_posts_responses_bodies,
    since_date,
)
from ..announcements import Announcement
from ..core import UrlType
from ..discord import ChannelsList, DiscordChannel
from ..fanbox import Fancard
from ..posts import ELEMENTS_PER_PAGE, Post, PostsList
from ..services import ServiceType

if TYPE_CHECKING:
    from ..core import UrlLike
    from ..services import ServiceLike
    from ..sessions import KemoSession

CreatorsList: TypeAlias = list["Creator"]
_CreatorFields: TypeAlias = Literal["id", "name", "service", "indexed", "updated",
                                    "public_id", "favorited"]
CreatorDict: TypeAlias = dict[_CreatorFields, Union[str, int, None]]
AnnouncementsList: TypeAlias = list[Announcement]
FancardsList: TypeAlias = list[Fancard]


@dataclass(kw_only=True)
class Creator:
    """
    Container class for a creator. Mainly initialized when using helper functions like
    :func:`.get_creator()`.

    :param id: It is the ID of the creator.
    :param name: It is the given name of the creator.
    :param service: The service that provides the content.
    :param indexed: Datetime that expresses when the creator is indexed.
    :param updated: Datetime that expresses when the creator was last updated.
    :param public_id: The public ID that the creator shows.
    :param favorited: A integer displaying how many have favorited this creator.
    :param relation_id: The relation ID of this creator.

    :type id: :class:`str`
    :type name: Optional[:class:`str`]
    :type service: :class:`.ServiceType`
    :type indexed: :class:`datetime.datetime`
    :type updated: :class:`datetime.datetime`
    :type public_id: Optional[:class:`str`]
    :type favorited: Optional[:class:`int`]
    :type relation_id: Optional[:class:`int`]
    """

    id: str
    name: Optional[str]
    service: ServiceType
    indexed: datetime = field(repr=False)
    updated: datetime = field(repr=False)
    public_id: Optional[str] = field(repr=False)
    favorited: Optional[int] = field(repr=False)
    relation_id: Optional[int] = field(repr=False)

    # unloaded fields
    _announcements: AnnouncementsList = field(default_factory=list, init=False, repr=False)
    __ann_loaded: bool = field(default=False, init=False, repr=False)

    _fancards: FancardsList = field(default_factory=list, init=False, repr=False)
    __fanc_loaded: bool = field(default=False, init=False, repr=False)

    _channels: ChannelsList = field(default_factory=list, init=False, repr=False)
    __chan_loaded: bool = field(default=False, init=False, repr=False)

    __kemo_session: Optional["KemoSession"] = field(default=None, init=False, repr=False)


    @classmethod
    async def from_dict(cls, **fields: CreatorDict) -> "Creator":
        """
        Initializes a creator from a dictionary containing its properties.

        :return: An instance of a creator.
        :rtype: :class:`Creator`
        """

        return cls(
            id=fields.get("id", None) or fields.get("user"),
            name=fields.get("name", None),
            service=ServiceType(fields.get("service")),
            indexed=datetime.strptime(fields.get("indexed"), MILI_DATE_FMT),
            updated=datetime.strptime(fields.get("updated"), MILI_DATE_FMT),
            public_id=fields.get("public_id", None),
            favorited=fields.get("favorited", None),
            relation_id=fields.get("relation_id", None)
        )


    @classmethod
    async def from_profile(cls,
                           service: "ServiceLike",
                           creator_id: str,
                           kemo_session: "KemoSession") -> Optional["Creator"]:
        """
        Retrieves a creator using its profile info.

        :param service: The service of the creator.
        :param creator_id: The ID of the creator.
        :param session: The Kemono Session to use for its creation.

        :type service: :type:`.ServiceLike`
        :type creator_id: :class:`str`
        :type session: :class:`.KemoSession`

        :return: If the creator is found, retrieve and create a :class:`Creator` instance, otherwise return ``None``.
        :rtype: Optional[:class:`Creator`]
        """

        creator_response = await kemo_session.get(f"/{service}/user/{creator_id}/profile")

        if creator_response.status == 404:
            return None

        return (await Creator.from_dict(**(await creator_response.json()))).set_underlying_session(kemo_session)


    async def announcements(self) -> AnnouncementsList:
        """
        Gets a list of the creator's announcements, if any. Mainly relevant for
        Patreon service.

        :return: A list of the creator's announcements, if any.
        :rtype: list[:class:`.Announcement`]
        """

        if not self.__ann_loaded:
            self.__ann_loaded = True
            self._announcements = await self._fetch_announcements()

        return self._announcements


    async def fancards(self) -> FancardsList:
        """
        Gets a list of the fancards associated with this creator.

        .. note:: If not from a Fanbox service, it will return an empty list instead.

        :return: A list of the creator's fancards, if any.
        :rtype: list[:class:`.Fancard`]
        """

        if not self.__fanc_loaded:
            self.__fanc_loaded = True
            self._fancards = await self._fetch_fancards()

        return self._fancards


    async def channels(self) -> ChannelsList:
        """
        Gets all the Discord channels associated with this creator.
        This is because the ID of a Discord 'creator', is really the ID of a Discord server/guild.

        .. note:: Only really works if the service is Discord, returns an empty list if not.

        :return: A list of the creator's associated Discord channels, if any.
        :rtype: list[:class:`.DiscordChannel`]
        """

        if not self.__chan_loaded:
            self.__chan_loaded = True
            self._channels = await self.fetch_channels()

        return self._channels


    @property
    def url(self) -> "UrlLike":
        """
        :return: The full URL of the creator.
        :rtype: :type:`.UrlLike`
        """

        return f"{UrlType.SITE}/{self.service}/user/{self.id}"


    async def other_links(self) -> list["Creator"]:
        """
        Searches for other accounts of this creator.

        :returns: Other instances of :class:`.Creator` associated to this one, if any. Might also
                  be an empty list if there is no session assigned.
        :rtype: list[:class:`.Creator`]
        """

        if self.__kemo_session is None:
            return []

        link_response = await self.__kemo_session.get(f"/{self.service}/user/{self.id}/links")
        links_tasks = []

        async for link_fields in link_response.json():
            links_tasks.append(
                Creator.from_profile(link_fields.get("service"),
                                     link_fields.get("id"),
                                     self.__kemo_session)
            )

        return [lnk for lnk in await gather(*links_tasks) if lnk is not None]


    def set_underlying_session(self, ks: "KemoSession") -> "Creator":
        """
        Quietly sets the session which the creator uses for its requests.
        
        :param session: The session instance.
        
        :type session: :class:`.KemoSession`

        :return: The same instance of the creator, for convenience.
        :rtype: :class:`.Creator`
        """

        self.__kemo_session = ks
        return self


    async def posts(self,
              *,
              query: Optional[str]=None,
              max_posts: Optional[int]=ELEMENTS_PER_PAGE,
              before: Optional[datetime]=None,
              since: Optional[datetime]=None) -> PostsList:
        """
        Retrieves posts under this creator. If the creator is from Discord, it won't retrieve any,
        as that service doesn't use 'posts'.

        :param query: The string to search for specific posts.
        :param max_posts: The max number of posts to look through. This is NOT necessarily the number of posts to enter the lists. If `None`, it will try to retrieve ALL the posts.
        :param before: Include only posts before this date.
        :param since: Include only posts after and including this date.

        :type query: Optional[:class:`str`]
        :type max_posts: Optional[:class:`int`]
        :type before: Optional[:class:`datetime.datetime`]
        :type since: Optional[:class:`datetime.datetime`]

        :raises ValueError: If ``max_posts`` is negative or zero.

        :return: A list of posts that fit the filters. Might be empty if there is no session assigned.
        :rtype: list[:class:`.Post`]
        """

        if max_posts is not None and max_posts <= 0:
            raise ValueError(f"max_posts must be an integer greater than zero, not '{max_posts}'")

        if self.__kemo_session is None:
            return []

        posts_tasks = []

        for post_fields in await get_posts_responses_bodies(
            endpoint=f"/{self.service}/user/{self.id}",
            query=query,
            max_posts=max_posts,
            page_stepping=ELEMENTS_PER_PAGE,
            kemo_session=self.__kemo_session
        ):
            published_str = post_fields["published"]
            if ((before is not None and not before_date(published_str, before)) or
                (since is not None and not since_date(published_str, since))):
                continue

            post_fields.update(creator=self)
            posts_tasks.append(add_session_to_post(Post.from_dict(**post_fields),
                                                   self.__kemo_session))

        return await gather(*posts_tasks)


    async def get_post(self, post_id: str) -> Optional[Post]:
        """
        Get a specific post by its ID.

        :param post_id: The ID of the post in question.

        :type post_id: :class:`str`

        :return: The post, if found. Otherwise returns ``None``.
        :rtype: Optional[`.Post`]
        """

        if self.__kemo_session is None:
            return None

        response = await self.__kemo_session.get(f"/{self.service}/user/{self.id}/post/{post_id}")

        if response.status == 404:
            return None

        return await add_session_to_post(Post.from_dict(**(await response.json()).get("post")),
                                         self.__kemo_session)


    async def _fetch_announcements(self) -> AnnouncementsList:
        """
        .. warning:: `(for internal purposes)`
        Fetches a request with the creator's announcements. This means that, unlike
        :meth:`.announcements()`, this reloads the announcements again.

        :return: A list of announcements. Might be empty if there is no session assigned.
        :rtype: list[:class:`.Announcement`]
        """

        if self.__kemo_session is None:
            return []

        response = await self.__kemo_session.get(f"/{self.service}/user/{self.id}/announcements")
        announcements_tasks = []

        async for ann_fields in response.json():
            ann_fields.update(creator=self)
            announcements_tasks.append(Announcement.from_dict(**ann_fields))

        return await gather(*announcements_tasks)


    async def _fetch_fancards(self) -> FancardsList:
        """
        .. warning:: `(for internal purposes)`
        Fetches a request with the creator's fancards. Unlike :meth:`.fancards()`,
        this reloads the fancards again.
        .. note:: If the service is not Fanbox, it will return an empty list instead.

        :return: A list of fancards. Might also be empty if there is not session assigned.
        :rtype: list[:class:`.Fancard`]
        """

        fancards = []

        if self.__kemo_session is not None and self.service == ServiceType.FANBOX:
            response = await self.__kemo_session.get(f"/{self.service}/user/{self.id}/fancards")
            fancards_tasks = []

            async for fancard_fields in response.json():
                fancard_fields.update(creator=self)
                fancards_tasks.append(Fancard.from_dict(**fancard_fields))

            fancards.extend(await gather(*fancards_tasks))

        return fancards


    async def fetch_channels(self) -> ChannelsList:
        """
        Fetches a request for Discord channels, if available. 

        :return: A list of channels. Might also be empty if there is no session assigned.
        :rtype: list[:class:`.DiscordChannel`]
        """

        channels = []

        if self.__kemo_session is not None and self.service == ServiceType.DISCORD:
            response = await self.__kemo_session.get(f"/discord/channel/lookup/{self.id}")
            channels_tasks = []

            async def add_session_to_channel(
                    chan_task: Coroutine[Any, Any, DiscordChannel]) -> DiscordChannel:
                return (await chan_task).set_underlying_session(self.__kemo_session)

            async for chan_fields in response.json():
                chan_fields.update(creator=self)
                channels_tasks.append(add_session_to_channel(DiscordChannel.from_dict(**chan_fields)))

            channels.extend(await gather(*channels_tasks))

        return channels


    async def get_channel(self, channel_id: str) -> Optional[DiscordChannel]:
        """
        Fetches a specific channel of this creator by id.

        :param channel_id: The ID of the channel to find.

        :type channel_id: :class:`str`

        :return: The channel in question, if found. Otherwise returns ``None``.
        :rtype: Optional[:class:`.DiscordChannel`]
        """

        response = await self.__kemo_session.get(f"/discord/channel/lookup/{self.id}")

        async for chan_fields in response.json():
            if chan_fields.get("id") == channel_id:
                chan_fields.update(creator=self)
                return (await DiscordChannel.from_dict(**chan_fields)).set_underlying_session(self.__kemo_session)

        return None