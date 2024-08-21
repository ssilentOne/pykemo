"""
Discord users module.
"""

from dataclasses import dataclass, field
from typing import Any, Optional

from ..core import UrlType
from ..files import File


@dataclass(kw_only=True)
class DiscordUser:
    """
    A discord user. Has different properties than that of `Creator`.

    id: The ID of the Discord user. The same the Discord API uses.
    username: The specific username that the user utilizes in this guild.
    global_name: The global name the Discord user has.
    discriminator: The discriminator of the Discord user, if any (they are not really used anymore).
    avatar: The avatar file.
    avatar_decoration_data: Aditional avatar info.
    clan: I guess this refers to the HypeSquad clans.
    accent_color: The accent color that the user chooses.
    banner: The banner of the user profile.
    banner_color: The accent color for the banner itself.
    flags: The flags in this guild.
    public_flags: The flags globally.
    """

    id: str
    username: str
    global_name: str
    discriminator: str
    avatar: File = field(repr=False)
    avatar_decoration_data: Optional[Any] = field(default=None, repr=False)
    clan: Optional[Any] = field(default=None, repr=False)
    accent_color: Optional[str] = field(default=None, repr=False)
    banner: Optional[Any] = field(default=None, repr=False)
    banner_color: Optional[str] = field(default=None, repr=False)
    flags: int = field(default=0, repr=False)
    public_flags: int = field(default=0, repr=False)


    @classmethod
    def from_dict(cls, **fields) -> "DiscordUser":
        """
        Initializes a DiscordUser instance from a response fields.
        """

        user_id = fields.get("id")
        username = fields.get("username")

        avatar_subpath = fields.get("avatar")
        avatar = File(name=f"{username}_avatar.png",
                      path=f"/avatars/{user_id}/{avatar_subpath}",
                      url_source=UrlType.DISCORD)


        return cls(
            id=user_id,
            username=username,
            global_name=fields.get("global_name"),
            discriminator=fields.get("discriminator"),
            avatar=avatar,
            avatar_decoration_data=fields.get("avatar_decoration_data", None),
            clan=fields.get("clan", None),
            accent_color=fields.get("accent_color", None),
            banner=fields.get("banner", None),
            banner_color=fields.get("banner_color", None),
            flags=fields.get("flags", 0),
            public_flags=fields.get("public_flags", 0)
        )
