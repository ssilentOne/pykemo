"""
Fancards module. Exclusive to Fanbox service.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from ..files import File

if TYPE_CHECKING:
    from ..creators import Creator

FANC_DATE_FMT: str = r"%Y-%m-%dT%H:%M:%S.%f"


@dataclass(kw_only=True)
class Fancard:
    """
    A Fancard is an exclusive feature of the Fanbox service, in which each supporter can
    hold a 'card' to show proof of their support to the creator.
    They have an image inside and as such their working are similar to the `File` type, but
    they both have different fields.

    id: The ID of this fancard.
    creator_id: The ID of this fancard's creator.
    creator: The creator of this fancard.
    file_id: The ID of this fancard's associated file.
    file_size: The size of the fancard's file size.
    file: The file of this fancard.
    price: General price tag for the tier this fancard belongs to.
    fhash: The hash of this fancard.
    ihash: The iterative hash of this fancard. Usually `None`.
    last_checked: When was this fancard last revised.
    added: When was this fancard first added.
    mtime: Dark magic. Dunno why it's there, but data is data, I guess.
    ctime: Dark magic. Dunno why it's there, but data is data, I guess.
    """

    id: str
    creator_id: str
    creator: "Creator" = field(repr=False)
    file_id: str
    file_size: int
    file: File = field(repr=False)
    price: str = field(repr=False)
    fhash: str = field(repr=False)
    ihash: Optional[str] = field(default=None, repr=False)
    last_checked: datetime = field(repr=False)
    added: datetime = field(repr=False)
    mtime: datetime = field(repr=False)
    ctime: datetime = field(repr=False)


    @classmethod
    def from_dict(cls, **fields) -> "Fancard":
        """
        Initializes a Fancard instance from a response fields.
        """

        creator: "Creator" = fields.get("creator")
        fhash = fields.get("hash")
        file_id = str(fields.get("file_id"))
        file_type = fields.get("mime")
        file_ext = fields.get("ext")

        file_name = f"{creator.name}_{file_id}{file_ext}"
        file_subpath = f"/{fhash[0:2]}/{fhash[2:4]}/{fhash}{file_ext}"

        return cls(
            id=str(fields.get("id")),
            creator_id=fields.get("user_id"),
            creator=creator,
            file_id=file_id,
            file_size=fields.get("size"),
            file=File(name=file_name, path=file_subpath, content_type=file_type),
            price=fields.get("price", ""),
            fhash=fhash,
            ihash=fields.get("ihash", None),
            last_checked=datetime.strptime(fields.get("last_checked_at"), FANC_DATE_FMT),
            added=datetime.strptime(fields.get("added"), FANC_DATE_FMT),
            mtime=datetime.strptime(fields.get("mtime"), FANC_DATE_FMT),
            ctime=datetime.strptime(fields.get("ctime"), FANC_DATE_FMT)
        )
