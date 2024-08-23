"""
Creators module.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Literal, Optional, TypeAlias, Union

from .._aux import (
    async_get_posts_responses,
    before_date,
    get_posts_responses,
    since_date,
)
from ..announcements import Announcement
from ..core import UrlType, get
from ..discord import ChannelsList, DiscordChannel
from ..fanbox import Fancard
from ..posts import DEFAULT_DATE_FMT, ELEMENTS_PER_PAGE, Post, PostsList
from ..services import ServiceType

if TYPE_CHECKING:
    from requests import Response

    from ..core import UrlLike
    from ..services import ServiceLike

CreatorsList: TypeAlias = list["Creator"]
_CreatorFields: TypeAlias = Literal["id", "name", "service", "indexed", "updated",
                                    "public_id", "favorited"]
CreatorDict: TypeAlias = dict[_CreatorFields, Union[str, int, None]]
AnnouncementsList: TypeAlias = list[Announcement]
FancardsList: TypeAlias = list[Fancard]


@dataclass(kw_only=True)
class Creator:
    """
    Container class for a creator.

    :param id: It is the ID of the creator.
    :param name: It is the given name of the creator.
    :param service: The service that provides the content.
    :param indexed: Datetime that expresses when the creator is indexed.
    :param updated: Datetime that expresses when the creator was last updated.
    :param public_id: The public ID that the creator shows.
    :param favorited: A integer displaying how many have favorited this creator.

    :type id: :class:`str`
    :type name: Optional[:class:`str`]
    :type service: :class:`.ServiceType`
    :type indexed: :class:`datetime.datetime`
    :type updated: :class:`datetime.datetime`
    :type public_id: Optional[:class:`str`]
    :type favorited: Optional[:class:`int`]
    """

    id: str
    name: Optional[str]
    service: ServiceType
    indexed: datetime = field(repr=False)
    updated: datetime = field(repr=False)
    public_id: Optional[str] = field(repr=False)
    favorited: Optional[int] = field(repr=False)

    #unloaded fields
    _announcements: AnnouncementsList = field(default_factory=list, init=False, repr=False)
    __ann_loaded: bool = field(default=False, init=False, repr=False)

    _fancards: FancardsList = field(default_factory=list, init=False, repr=False)
    __fanc_loaded: bool = field(default=False, init=False, repr=False)

    _channels: ChannelsList = field(default_factory=list, init=False, repr=False)
    __chan_loaded: bool = field(default=False, init=False, repr=False)


    @classmethod
    def from_dict(cls, **fields: CreatorDict) -> "Creator":
        """
        Initializes a creator from a dictionary containing its properties.

        :return: An instance of a creator.
        :rtype: :class:`Creator`
        """

        date_fmt = rf"{DEFAULT_DATE_FMT}.%f"

        return cls(
            id=fields.get("id", None) or fields.get("user"),
            name=fields.get("name", None),
            service=ServiceType(fields.get("service")),
            indexed=datetime.strptime(fields.get("indexed"), date_fmt),
            updated=datetime.strptime(fields.get("updated"), date_fmt),
            public_id=fields.get("public_id", None),
            favorited=fields.get("favorited", None)
        )


    @classmethod
    def from_profile(cls, service: "ServiceLike", creator_id: str) -> Optional["Creator"]:
        """
        Retrieves a creator using its profile info.

        :param service: The service of the creator.
        :param creator_id: The ID of the creator.

        :type service: :type:`ServiceLike`
        :type creator_id: :class:`str`

        :return: If the creator is found, retrieve and create a :class:`Creator` instance, otherwise return ``None``.
        :rtype: Optional[:class:`Creator`]
        """

        creator_response = get(f"/{service}/user/{creator_id}/profile")

        if creator_response.status_code == 404:
            return None

        return Creator.from_dict(**creator_response.json())


    @property
    def announcements(self) -> AnnouncementsList:
        """
        Gets a list of the creator's announcements, if any. Mainly relevant for
        Patreon service.

        :return: A list of the creator's announcements, if any.
        :rtype: list[:class:`.Announcement`]
        """

        if not self.__ann_loaded:
            self.__ann_loaded = True
            self._announcements = self._fetch_announcements()

        return self._announcements


    @property
    def fancards(self) -> FancardsList:
        """
        Gets a list of the fancards associated with this creator.

        .. note:: If not from a Fanbox service, it will return an empty list instead.

        :return: A list of the creator's fancards, if any.
        :rtype: list[:class:`.Fancard`]
        """

        if not self.__fanc_loaded:
            self.__fanc_loaded = True
            self._fancards = self._fetch_fancards()

        return self._fancards


    @property
    def channels(self) -> ChannelsList:
        """
        Gets all the Discord channels associated with this creator.
        This is because the ID of a Discord 'creator', is really the ID of a Discord server/guild.

        .. note:: Only really works if the service is Discord, returns an empty list if not.

        :return: A list of the creator's associated Discord channels, if any.
        :rtype: list[:class:`.DiscordChannel`]
        """

        if not self.__chan_loaded:
            self.__chan_loaded = True
            self._channels = self.fetch_channels()

        return self._channels


    @property
    def url(self) -> "UrlLike":
        """
        :return: The full URL of the creator.
        :rtype: :type:`.UrlLike`
        """

        return f"{UrlType.SITE}/{self.service}/user/{self.id}"


    def other_links(self) -> list["Creator"]:
        """
        Searches for other accounts of this creator.

        :returns: Other instances of :class:`.Creator` associated to this one, if any.
        :rtype: list[:class:`.Creator`]
        """

        link_response = get(f"/{self.service}/user/{self.id}/links")
        links = []

        for link_fields in link_response.json():
            creator = Creator.from_profile(link_fields.get("service"),
                                           link_fields.get("id"))
            if creator is not None:
                links.append(creator)

        return links


    def posts(self,
              *,
              query: Optional[str]=None,
              max_posts: Optional[int]=ELEMENTS_PER_PAGE,
              before: Optional[datetime]=None,
              since: Optional[datetime]=None,
              asynchronous: bool=False) -> PostsList:
        """
        Retrieves posts under this creator. If the creator is from Discord, it won't retrieve any,
        as that service doesn't use 'posts'.

        :param query: The string to search for specific posts.
        :param max_posts: The max number of posts to look through. This is NOT necessarily the number of posts to enter the lists. If `None`, it will try to retrieve ALL the posts.
        :param before: Include only posts before this date.
        :param since: Include only posts after and including this date.
        :param asynchronous: Wether to use asynchronous requests to maybe boost performance. It's really only recommended with queries of no more than 350 posts. Too many queries overwhelms the server and it actually slows the request down.

        :type query: Optional[:class:`str`]
        :type max_posts: Optional[:class:`int`]
        :type before: Optional[:class:`datetime.datetime`]
        :type since: Optional[:class:`datetime.datetime`]
        :type asynchronous: :class:`bool`

        :raises ValueError: If ``max_posts`` is negative or zero.

        :return: A list of posts that fit the filters.
        :rtype: list[:class:`.Post`]
        """

        if max_posts is not None and max_posts <= 0:
            raise ValueError(f"max_posts must be an integer greater than zero, not '{max_posts}'")

        posts_req = (async_get_posts_responses if asynchronous else get_posts_responses)
        response_bodies = posts_req(endpoint=f"/{self.service}/user/{self.id}",
                                    query=query,
                                    max_posts=max_posts,
                                    page_stepping=ELEMENTS_PER_PAGE)
        posts_list = []

        for post_fields in response_bodies:
            published_str = post_fields["published"]
            if ((before is not None and not before_date(published_str, before)) or
                (since is not None and not since_date(published_str, since))):
                continue

            post_fields.update(creator=self)
            post = Post.from_dict(**post_fields)

            posts_list.append(post)

        return posts_list


    def get_post(self, post_id: str) -> Optional[Post]:
        """
        Get a specific post by its ID.

        :param post_id: The ID of the post in question.

        :type post_id: :class:`str`

        :return: The post, if found. Otherwise returns ``None``.
        :rtype: Optional[`.Post`]
        """

        response = get(f"/{self.service}/user/{self.id}/post/{post_id}")

        if response.status_code == 404:
            return None

        return Post.from_dict(**response.json())


    def _fetch_announcements(self) -> AnnouncementsList:
        """
        .. warning:: `(for internal purposes)`
        Fetches a request with the creator's announcements. This means that, unlike
        :attr:`.announcements`, this reloads the announcements again.

        :return: A list of announcements.
        :rtype: list[:class:`.Announcement`]
        """

        response = get(f"/{self.service}/user/{self.id}/announcements")
        announcements = []

        for ann_fields in response.json():
            ann_fields.update(creator=self)
            announcements.append(Announcement.from_dict(**ann_fields))

        return announcements


    def _fetch_fancards(self) -> FancardsList:
        """
        .. warning:: `(for internal purposes)`
        Fetches a request with the creator's fancards. Unlike :attr:`.fancards`,
        this reloads the fancards again.
        .. note:: If the service is not Fanbox, it will return an empty list instead.

        :return: A list of fancards.
        :rtype: list[:class:`.Fancard`]
        """

        fancards = []

        if self.service == ServiceType.FANBOX:
            response = get(f"/{self.service}/user/{self.id}/fancards")

            for fancard_fields in response.json():
                fancard_fields.update(creator=self)
                fancards.append(Fancard.from_dict(**fancard_fields))

        return fancards


    def _get_channels_response(self) -> "Response":
        """
        .. warning:: `(for internal purposes)`
        Gets the channels request.

        :return: The response of the channels' lookup.
        :rtype: `Response <https://requests.readthedocs.io/en/latest/api/#requests.Response>`_
        """

        return get(f"/discord/channel/lookup/{self.id}")


    def fetch_channels(self) -> ChannelsList:
        """
        Fetches a request for Discord channels, if available. 

        :return: A list of channels.
        :rtype: list[:class:`.DiscordChannel`]
        """

        channels = []

        if self.service == ServiceType.DISCORD:

            for chan_fields in self._get_channels_response().json():
                chan_fields.update(creator=self)
                channels.append(DiscordChannel.from_dict(**chan_fields))


        return channels


    def get_channel(self, channel_id: str) -> Optional[DiscordChannel]:
        """
        Fetches a specific channel of this creator by id.

        :param channel_id: The ID of the channel to find.

        :type channel_id: :class:`str`

        :return: The channel in question, if found. Otherwise returns ``None``.
        :rtype: Optional[:class:`.DiscordChannel`]
        """

        for chan_fields in self._get_channels_response().json():
            if chan_fields.get("id") == channel_id:
                chan_fields.update(creator=self)
                return DiscordChannel.from_dict(**chan_fields)

        return None