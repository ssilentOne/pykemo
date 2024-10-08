"""
Discord messages module.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Optional, TypeAlias

from .._aux import sanitize_data_url
from ..files import File, FilesList
from .users import DiscordUser

if TYPE_CHECKING:
    from .channels import DiscordChannel

MessagesList: TypeAlias = list["DiscordMessage"]

MSG_DATE_FMT = r"%Y-%m-%dT%H:%M:%S.%f"


@dataclass(kw_only=True)
class DiscordMessage:
    """
    A discord message inside a channel.

    :param id: The ID of the message itself.
    :param author: The user that authored the message
    :param server_id: The ID of the server this messages lives in.
    :param channel: The channel where this message is within the server.
    :param content: The actual text contents of the message.
    :param added: When was the message added to the database that this API refers to.
    :param published: When was the message originally published.
    :param edited: When was this message edited, if it ever was.
    :param embeds: List of embeds of the message.
    :param mentions: List of potential mentions the message makes.
    :param attachments: The files this message has.

    :type id: :class:`str`
    :type author: Optional[:class:`.DiscordUser`]
    :type server_id: :class:`str`
    :type channel: :class:`.DiscordChannel`
    :type content: :class:`str`
    :type added: Optional[:class:`datetime.datetime`]
    :type published: :class:`datetime.datetime`
    :type edited: Optional[:class:`datetime.datetime`]
    :type embeds: :class:`list`
    :type mentions: :class:`list`
    :type attachments: list[:class:`File`]
    """

    id: str
    author: Optional[DiscordUser] = field(default=None, repr=False)
    server_id: str
    channel: "DiscordChannel" = field(repr=False)
    content: str = field(repr=False)
    added: Optional[datetime] = field(default=None, repr=False)
    published: datetime = field(repr=False)
    edited: Optional[datetime] = field(default=None, repr=False)
    embeds: list = field(default_factory=list, repr=False)
    mentions: list = field(default_factory=list, repr=False)
    attachments: FilesList = field(default_factory=list, repr=False)


    @classmethod
    def from_dict(cls, **fields) -> "DiscordMessage":
        """
        Initializes a DiscordMessage instance from a response fields.

        :return: A message instance.
        :rtype: :class:`.DiscordMessage`
        """

        author_fields = fields.get("author", None)
        added_date = fields.get("added", None)
        edited_date = fields.get("edited", None)

        return cls(
            id=fields.get("id"),
            author=(DiscordUser.from_dict(**author_fields) if author_fields is not None else None),
            server_id=fields.get("server"),
            channel=fields.get("parent_channel"),
            content=fields.get("content", ""),
            added=(datetime.strptime(added_date, MSG_DATE_FMT) if added_date is not None else None),
            published=datetime.strptime(fields.get("published"), MSG_DATE_FMT),
            edited=(datetime.strptime(edited_date, MSG_DATE_FMT)
                    if edited_date is not None else None),
            embeds=fields.get("embeds", []),
            mentions=fields.get("mentions", []),
            attachments=[File.from_dict(**sanitize_data_url(attachment_fields))
                         for attachment_fields in fields.get("attachments")]
        )


    def before(self, date: datetime) -> bool:
        """
        Verifies if the message was published before a certain date.

        :param date: The date to evaluate.

        :type date: :class:`datetime.datetime`

        :return: The result of ``DiscordMessage.published < date``
        :rtype: :class:`bool`
        """

        return self.published < date


    def since(self, date: datetime) -> bool:
        """
        Verifies if the message was published after a certain date.

        :param date: The date to evaluate.

        :type date: :class:`datetime.datetime`

        :return: The result of ``DiscordMessage.published < date``
        :rtype: :class:`bool`
        """

        return self.published >= date
