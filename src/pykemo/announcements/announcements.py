"""
Announcements module.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING

from ..services import ServiceType

if TYPE_CHECKING:
    from ..creators import Creator

ANN_DATE_FMT: str = r"%Y-%m-%dT%H:%M:%S.%f"
"The default format for announcements dates."


@dataclass(kw_only=True)
class Announcement:
    """
    Announcement tied to a creator. Mainly used in users with Patreon service.
    Instances of this class are usually created through :attr:`.Creator.announcements`.

    :param service: The service of the creator that made this announcement. Tipically Patreon.
    :param creator_id: The id of this announcement's creator.
    :param ann_hash: The hash of the announcement.
    :param content: The actual contents of the announcement. May contain HTML tags.
    :param added: When was this announcement made.
    :param creator: The creator of this announcement.

    :type service: :class:`.ServiceType`
    :type creator_id: :class:`str`
    :type ann_hash: :class:`str`
    :type content: :class:`str`
    :type added: :class:`datetime.datetime`
    :type creator: :class:`.Creator`
    """

    service: ServiceType
    creator_id: str
    ann_hash: str = field(repr=False)
    content: str = field(repr=False)
    added: datetime = field(repr=False)
    creator: "Creator" = field(repr=False)


    @classmethod
    def from_dict(cls, **fields) -> "Announcement":
        """
        Initializes an Announcement instance from a response fields.

        :return: An instace of an announcement.
        :rtype: :class:`.Announcement`
        """

        return cls(
            service=ServiceType(fields.get("service")),
            creator_id=fields.get("user_id"),
            ann_hash=fields.get("hash"),
            content=fields.get("content", ""),
            added=datetime.strptime(fields.get("added"), ANN_DATE_FMT),
            creator=fields.get("creator")
        )
