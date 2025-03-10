"""
Discord channels module.
"""

from asyncio import gather
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Optional, TypeAlias

from .._aux import (
    MILI_DATE_FMT,
    add_session_to_message,
    before_date,
    get_posts_responses_bodies,
    since_date,
)
from ..core import UrlType
from .messages import DiscordMessage, MessagesList

if TYPE_CHECKING:
    from ..core import UrlLike
    from ..creators import Creator
    from ..sessions import KemoSession

ChannelsList: TypeAlias = list["DiscordChannel"]

OFFSET_STEPPING: int = 150
"Offset stepping enforced by the API when querying Discord channels."


@dataclass(kw_only=True)
class DiscordChannel:
    """
    A channel that belongs to a Discord server/guild.

    :param id: The ID of the channel. The same the Discord API uses.
    :param channel_name: The display name of the channel.
    :param owner: The creator that owns this server. Its ID is the same as the creator's.

    :type id: :class:`str`
    :type channel_name: :class:`str`
    :type owner: :class:`.Creator`
    """

    id: str
    channel_name: str
    owner: "Creator" = field(repr=False)

    __kemo_session: Optional["KemoSession"] = field(default=None, init=False, repr=False)


    @classmethod
    async def from_dict(cls, **fields) -> "DiscordChannel":
        """
        Initializes a DiscordChannel instance from a response fields.

        :return: A channel instance.
        :rtype: :class:`.DiscordChannel`
        """

        return cls(
            id=fields.get("id"),
            channel_name=fields.get("name"),
            owner=fields.get("creator")
        )


    @property
    def server_id(self) -> str:
        """
        The ID of the server this channel lives in. By definition, it's the same
        as the creator's ID.

        :return: The server's `(the creator's, really)` ID.
        :rtype: :class:`str`
        """

        return self.owner.id


    @property
    def url(self) -> "UrlLike":
        """
        Retrieves the URL of the channel.

        :return: The full URL of the channel.
        :rtype: :type:`.urlLike`
        """

        return f"{UrlType.SITE}/discord/server/{self.server_id}#{self.id}"


    def set_underlying_session(self, ks: "KemoSession") -> "DiscordChannel":
        """
        Quietly sets the session which the channel uses for its requests.
        
        :param session: The session instance.
        
        :type session: :class:`.KemoSession`

        :return: The same instance of the channel, for convenience.
        :rtype: :class:`.Creator`
        """

        self.__kemo_session = ks
        return self


    async def messages(self,
                 *,
                 max_msg: Optional[int]=None,
                 before: Optional[datetime]=None,
                 since: Optional[datetime]=None) -> MessagesList:
        """
        Retrieve the messages of this channel.

        :param max_msg: The max number of posts to look through. This is NOT necessarily the number
                        of posts to enter the lists.
        :param before: Include only posts before this date.
        :param since: Include only posts after and including this date.

        :type max_msg: Optional[:class:`int`]
        :type before: Optional[:class:`datetime.datetime`]
        :type since: Optional[:class:`datetime.datetime`]

        :return: A list of the messages of the channel that fit the filters. Might be empty if there is no session assigned.
        :rtype: list[:class:`.DiscordMessage`]
        """

        if max_msg is not None and max_msg <= 0:
            raise ValueError(f"max_msg must be an integer greater than zero, not '{max_msg}'")

        if self.__kemo_session is None:
            return []

        msgs_tasks = []

        async for msg_fields in get_posts_responses_bodies(
            endpoint=f"/discord/channel/{self.id}",
            max_posts=max_msg,
            page_stepping=OFFSET_STEPPING,
            kemo_session=self.__kemo_session
        ):
            published_str = msg_fields["published"]
            if ((before is not None and not before_date(published_str, before,
                                                        fmt1=MILI_DATE_FMT, fmt2=MILI_DATE_FMT)) or
                (since is not None and not since_date(published_str, since,
                                                      fmt1=MILI_DATE_FMT, fmt2=MILI_DATE_FMT))):
                continue

            msg_fields.update(parent_channel=self)
            msgs_tasks.append(add_session_to_message(DiscordMessage.from_dict(**msg_fields)), self.__kemo_session)

        return await gather(*msgs_tasks)
